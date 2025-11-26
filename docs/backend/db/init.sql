CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS carga_horas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recurso_id VARCHAR(50) NOT NULL,
    tarea_id VARCHAR(50) NOT NULL,
    proyecto_id VARCHAR(50) NOT NULL,
    cliente_id INTEGER,
    fecha DATE NOT NULL,
    -- REGLA DE NEGOCIO: Maximo 8 horas por carga individual
    horas DECIMAL(5,2) NOT NULL CHECK (horas > 0 AND horas <= 8),
    descripcion TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_carga_horas_recurso ON carga_horas(recurso_id);
CREATE INDEX idx_carga_horas_fecha ON carga_horas(fecha);
CREATE INDEX idx_carga_horas_proyecto ON carga_horas(proyecto_id);
CREATE INDEX idx_carga_horas_recurso_fecha ON carga_horas(recurso_id, fecha);

-- Funcion para validar el total diario (Regla de Negocio)
CREATE OR REPLACE FUNCTION validar_horas_diarias()
RETURNS TRIGGER AS $$
DECLARE 
    total_horas_diarias DECIMAL(5,2);
BEGIN
    SELECT COALESCE(SUM(horas), 0) INTO total_horas_diarias
    FROM carga_horas
    WHERE recurso_id = NEW.recurso_id 
        AND fecha = NEW.fecha
        AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000'::UUID);

    -- REGLA DE NEGOCIO: No mas de 8 horas TOTALES por dia
    IF (total_horas_diarias + NEW.horas > 8) THEN
        RAISE EXCEPTION 'No se puede cargar mas de 8 horas por dia';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validar_horas_diarias ON carga_horas;

CREATE TRIGGER trigger_validar_horas_diarias
BEFORE INSERT OR UPDATE ON carga_horas
FOR EACH ROW EXECUTE FUNCTION validar_horas_diarias();