"""
conftest.py es un archivo ESPECIAL de pytest. No se ejecuta como un test: pytest lo descubre automáticamente y 
pone lo que hay dentro (las "fixtures") a disposición de todos los tests de esta carpeta, sin necesidad de 
importarlo.
Contiene las funciones y fixtures necesarias para crear una sesión completamente de prueba de la app para 
realizar los tests de forma segura y confiable.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session


@pytest.fixture(name="session")         #name=session: cuando un test u otro fixture tenga un parametro session, se obtendrá por medio de esta función.
def session_fixture():

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    """
    Crear un motor en la ruta 'sqlite://' (sin archivo después de //) crea la BBDD en memoria, de forma que cuando 
    termina la función, ésta desaparece junto a su sesión.

    StaticPool + check_same_thread=False: necesarios para que una BBDD en memoria funcione con el TestClient (que 
    puede usar varios hilos). Sin esto, cada conexión vería una BBDD en memoria distinta y vacía.
    """

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):        #usa la fixture session. cada vez que se use esta fixture, se llamará a ésta también.
    """
    Entrega un TestClient para hacer peticiones a la app, pero con la BBDD real
    SUSTITUIDA por la de memoria del fixture 'session'.
    """

    # cambiamos la función que usa FASTAPI para obtener la dependencia de la sesión
    def get_session_override():
        yield session
    app.dependency_overrides[get_session] = get_session_override

    # creamos el TestClient capaz de hacer peticiones a la app.
    client = TestClient(app)
    yield client

    # cuando haya terminado la función del client, se reestablece la función de la dependencia.
    app.dependency_overrides.clear()


# --- Función auxiliar para no repetir el registro+login en cada test ---
def registrar_y_headers(client, username="ana", password="12345678"):       
    """Registra un usuario, inicia sesión y devuelve los headers con el token."""

    # creación del usuario de prueba y de un token
    client.post("/register", json={"username": username, "password": password})
    respuesta = client.post("/login", json={"username": username, "password": password})

    # devolver el token
    token = respuesta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
