from sqlmodel import SQLModel, create_engine, Session

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

"""
Se define la llamada a create_all en una función ya que si se ejecutase antes que la creación de las clases
en models.py no crearía nada.
Al llamarse desde el main forzando importar models antes, nos aseguramos de que se hayan creado.
"""


def get_session():
    with Session(engine) as session:
        yield session

"""
Inyectar la sesión de la BBDD como dependencia permite, además de clarificar el código, usar la misma sesión usada
en la otra dependencia (que ha obtenido el usuario) para la propia función. Esto, además de ser más eficiente, permite
usar relaciones y monitorear el usuario por el ORM de SQLModel.
"""