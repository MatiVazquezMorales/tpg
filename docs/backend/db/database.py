from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import sys
import os

# Ajustamos el path para importar config correctamente desde una subcarpeta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import DATABASE_URL

# Crear el motor de base de datos
# connect_args={"check_same_thread": False} solo es necesario para SQLite, no para Postgres
engine = create_engine(DATABASE_URL)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Generador de dependencias para FastAPI.
    Crea una nueva sesión de base de datos para cada request y la cierra al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()