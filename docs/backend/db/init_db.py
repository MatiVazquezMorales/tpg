"""
Script de inicialización de la base de datos.
Se ejecuta automáticamente al arrancar el backend para asegurar que el esquema esté creado.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Agregar el path del backend al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import DATABASE_URL

def init_database():
    """Inicializa la base de datos ejecutando el script init.sql"""
    try:
        # Leer el script SQL
        script_path = os.path.join(os.path.dirname(__file__), 'init.sql')
        
        if not os.path.exists(script_path):
            print(f"⚠️  Advertencia: No se encontró el archivo {script_path}")
            return False
        
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Conectar a la base de datos
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Inicializando base de datos...")
        
        # Ejecutar statements en orden, manejando funciones PL/pgSQL correctamente
        # Dividir por ';' pero solo cuando NO estamos dentro de un bloque $$
        import psycopg2
        from urllib.parse import urlparse
        
        # Parsear DATABASE_URL
        db_url = DATABASE_URL.replace('postgresql://', 'postgres://')
        parsed = urlparse(db_url)
        db_name = parsed.path[1:] if parsed.path.startswith('/') else (parsed.path or 'carga_horas')
        
        conn_psycopg = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=db_name,
            user=parsed.username,
            password=parsed.password
        )
        
        try:
            conn_psycopg.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn_psycopg.cursor()
            
            # Ejecutar statements manualmente en el orden correcto
            # 1. Extension
            try:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"⚠️  Extensión: {e}")
            
            # 2. Tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carga_horas (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    recurso_id VARCHAR(50) NOT NULL,
                    tarea_id VARCHAR(50) NOT NULL,
                    proyecto_id VARCHAR(50) NOT NULL,
                    cliente_id INTEGER,
                    fecha DATE NOT NULL,
                    horas DECIMAL(5,2) NOT NULL CHECK (horas > 0 AND horas <= 24),
                    descripcion TEXT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 3. Índices
            for idx_sql in [
                "CREATE INDEX IF NOT EXISTS idx_carga_horas_recurso ON carga_horas(recurso_id)",
                "CREATE INDEX IF NOT EXISTS idx_carga_horas_fecha ON carga_horas(fecha)",
                "CREATE INDEX IF NOT EXISTS idx_carga_horas_proyecto ON carga_horas(proyecto_id)",
                "CREATE INDEX IF NOT EXISTS idx_carga_horas_recurso_fecha ON carga_horas(recurso_id, fecha)"
            ]:
                try:
                    cursor.execute(idx_sql)
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Índice: {e}")
            
            # 4. Función (bloque completo)
            cursor.execute("""
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

                    IF (total_horas_diarias + NEW.horas > 24) THEN
                        RAISE EXCEPTION 'No se puede cargar mas de 24 horas por dia';
                    END IF;

                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql
            """)
            
            # 5. Trigger
            cursor.execute("DROP TRIGGER IF EXISTS trigger_validar_horas_diarias ON carga_horas")
            cursor.execute("""
                CREATE TRIGGER trigger_validar_horas_diarias
                BEFORE INSERT OR UPDATE ON carga_horas
                FOR EACH ROW EXECUTE FUNCTION validar_horas_diarias()
            """)
            
            cursor.close()
        except Exception as e:
            print(f"⚠️  Error: {e}")
        finally:
            conn_psycopg.close()
        
        print("✅ Base de datos inicializada correctamente")
        return True
        
    except OperationalError as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        print("   Asegúrate de que DATABASE_URL esté configurado correctamente")
        return False
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

if __name__ == "__main__":
    init_database()

