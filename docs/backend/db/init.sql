CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- IMPORTANTE: Si ya tenías la tabla creada con tipos UUID, 
-- primero debes borrarla ejecutando: DROP TABLE IF EXISTS carga_horas;

CREATE TABLE IF NOT EXISTS carga_horas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recurso_id VARCHAR(50) NOT NULL,       -- CAMBIADO: De UUID a VARCHAR para compatibilidad
    tarea_id VARCHAR(50) NOT NULL,         -- CAMBIADO: De UUID a VARCHAR
    proyecto_id VARCHAR(50) NOT NULL,      -- CAMBIADO: De UUID a VARCHAR
    cliente_id INTEGER,
    fecha DATE NOT NULL,
    horas DECIMAL(5,2) NOT NULL CHECK (horas > 0 AND horas <= 24),
    descripcion TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indices para manejar mas facil las consultas
CREATE INDEX idx_carga_horas_recurso ON carga_horas(recurso_id);
CREATE INDEX idx_carga_horas_fecha ON carga_horas(fecha);
CREATE INDEX idx_carga_horas_proyecto ON carga_horas(proyecto_id);
CREATE INDEX idx_carga_horas_recurso_fecha ON carga_horas(recurso_id, fecha);

-- Funcion para que no se inserten mas de 24 horas por dia en la BD

CREATE OR REPLACE FUNCTION validar_horas_diarias()
RETURNS TRIGGER AS $$
DECLARE 
    total_horas_diarias DECIMAL(5,2);
BEGIN
    SELECT COALESCE(SUM(horas), 0) INTO total_horas_diarias
    FROM carga_horas
    WHERE recurso_id = NEW.recurso_id 
        AND fecha = NEW.fecha
        -- Nota: El ID interno sigue siendo UUID, así que este cast es correcto
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID);

    IF (total_horas_diarias + NEW.horas > 24) THEN
        RAISE EXCEPTION 'No se puede cargar mas de 24 horas por dia';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Borramos el trigger si existe para evitar duplicados al recrear
DROP TRIGGER IF EXISTS trigger_validar_horas_diarias ON carga_horas;

CREATE TRIGGER trigger_validar_horas_diarias
BEFORE INSERT OR UPDATE ON carga_horas
FOR EACH ROW EXECUTE FUNCTION validar_horas_diarias();