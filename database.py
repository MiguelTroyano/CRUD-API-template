from sqlmodel import SQLModel, create_engine

#Creación de la base de datos
engine = create_engine("sqlite:///proyecto.db")         # crea o referencia si ya ha sido creada


"""
Esta forma de inciar la base de datos no permite hacer modificaciones en la estructura de las tablas (añadir/eliminar columnas,
cambiar tipo de columna, cambiar claves primarias o foráneas, etc.) una vez creadas. La solución para no tener que eliminar la base
de datos entera es escribir una MIGRACIÓN (Alembic para SQLAlchemy).
"""

def crear_tablas():
    import models       #importante para que pueda crear las tablas

    SQLModel.metadata.create_all(engine)                    # (se ejecuta solo si no ha sido creada)