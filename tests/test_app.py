"""
Tests de la aplicación.

pytest descubre automáticamente:
  - los archivos que empiezan por 'test_'
  - las funciones dentro que empiezan por 'test_'

Cada función de test recibe las fixtures que nombra en sus argumentos
(aquí 'client'), y pytest se encarga de construirlas antes de ejecutar el test.

Patrón que sigue cada test (AAA):
  - Arrange (preparar): montar los datos de partida
  - Act (actuar): hacer la acción que se prueba
  - Assert (afirmar): comprobar que el resultado es el esperado
Si un 'assert' es falso, el test FALLA y pytest te muestra qué esperabas vs qué salió.
"""
from conftest import registrar_y_headers        # no hace falta importar las fixtures
from sqlmodel import select
from models import Usuario


# ---------- Registro y login ----------

def test_registro_devuelve_id_y_username(client):
    respuesta = client.post("/register", json={"username": "ana", "password": "12345678"})

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["username"] == "ana"
    assert "hashed_password" not in datos      # NUNCA debe filtrarse el hash
    assert "password" not in datos             # mucho menos la contraseña


def test_registro_username_duplicado_falla(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    # segundo registro con el mismo nombre
    respuesta = client.post("/register", json={"username": "ana", "password": "otra1234"})

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Nombre de usuario ya en uso"
    """
    Incluir un mensaje en las aserciones no es una buena práctica ya que es algo que, a la que cambie por
    cualquier convencionalidad, requiere un cambio tedioso en los tests también.
    """


def test_registro_password_corta_falla(client, session):
    respuesta = client.post("/register", json={"username": "ana", "password": "cinco"})

    assert respuesta.status_code == 422
    assert session.exec(select(Usuario).where(Usuario.username == "ana")).first() is None

def test_registro_username_corto_falla(client):
    respuesta = client.post("/register", json={"username": "ab", "password": "12345678"})
    assert respuesta.status_code == 422


def test_login_correcto_devuelve_token(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    respuesta = client.post("/login", json={"username": "ana", "password": "12345678"})

    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()


def test_login_password_incorrecta_da_401(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    respuesta = client.post("/login", json={"username": "ana", "password": "MALA1234"})

    assert respuesta.status_code == 401
    assert "access_token" not in respuesta.json()
    assert respuesta.json()["detail"] == "Usuario o contraseña incorrectos"


def test_login_usuario_inexistente_da_401(client):
    respuesta = client.post("/login", json={"username": "fantasma", "password": "12345678"})

    assert respuesta.status_code == 401
    assert "access_token" not in respuesta.json()
    assert respuesta.json()["detail"] == "Usuario o contraseña incorrectos"


def test_username_se_normaliza_a_minusculas(client):
    # registro con mayúsculas...
    client.post("/register", json={"username": "Ana", "password": "12345678"})
    # ...y login escribiéndolo distinto: debe encontrar la cuenta
    respuesta = client.post("/login", json={"username": "ANA", "password": "12345678"})
    assert respuesta.status_code == 200
    assert "access_token" in respuesta.json()


def test_username_duplicado_ignorando_mayusculas(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})
    # intentar registrar "Ana" debe chocar con la unicidad (ambos son "ana")
    respuesta = client.post("/register", json={"username": "Ana", "password": "otra1234"})
    assert respuesta.status_code == 400


def test_login_password_corta_da_401_no_422(client):
    client.post("/register", json={"username": "ana", "password": "correcta123"})
    # intento de login con contraseña corta y equivocada
    respuesta = client.post("/login", json={"username": "ana", "password": "no"})
    assert respuesta.status_code == 401       # no 422: el login no aplica reglas de longitud

# ---------- Autorización ----------

def test_listar_objetos_sin_token_da_401(client):
    respuesta = client.get("/objetos")

    assert respuesta.status_code == 401
    """
    Al no haber token, el error ocurre en la propia llamada a la dependencia de autorización, que tiene una 
    dependencia de seguridad que falla al no tener 'Authorization' en sus headers.
    (No se lanza el error personalizado)
    """


# ---------- CRUD de objetos ----------

def test_crear_objeto_lo_asigna_al_usuario(client):
    headers = registrar_y_headers(client)

    respuesta = client.post("/objetos", json={"title": "pan"}, headers=headers)

    assert respuesta.status_code == 201
    objeto = respuesta.json()
    assert objeto["title"] == "pan"
    assert objeto["done"] is False


def test_crear_objeto_titulo_vacio_falla(client):
    headers = registrar_y_headers(client)
    respuesta = client.post("/objetos", json={"title": ""}, headers=headers)
    assert respuesta.status_code == 422


def test_crear_objeto_solo_espacios_falla(client):
    headers = registrar_y_headers(client)
    respuesta = client.post("/objetos", json={"title": "   "}, headers=headers)
    assert respuesta.status_code == 422


def test_crear_objeto_recorta_espacios(client):
    headers = registrar_y_headers(client)
    respuesta = client.post("/objetos", json={"title": "  con espacios  "}, headers=headers)
    assert respuesta.status_code == 201
    assert respuesta.json()["title"] == "con espacios"      # guardado sin los espacios de los bordes


def test_listar_devuelve_los_objetos_creados(client):
    headers = registrar_y_headers(client)
    client.post("/objetos", json={"title": "obj 1"}, headers=headers)
    client.post("/objetos", json={"title": "obj 2"}, headers=headers)

    respuesta = client.get("/objetos", headers=headers)

    assert respuesta.status_code == 200
    objs = [(o["title"], o["done"]) for o in respuesta.json()]
    assert objs == [("obj 1", False), ("obj 2", False)]


def test_marcar_done(client):
    headers = registrar_y_headers(client)
    creado = client.post("/objetos", json={"title": "tarea"}, headers=headers).json()

    respuesta = client.put(f"/objetos/{creado['id']}", json={"done": True}, headers=headers)

    assert respuesta.status_code == 200
    assert respuesta.json()["done"] is True


def test_actualizar_titulo_demasiado_largo_falla(client):
    headers = registrar_y_headers(client)
    creado = client.post("/objetos", json={"title": "obj"}, headers=headers).json()

    respuesta = client.put(f"/objetos/{creado['id']}",
                           json={"title": "x" * 200},
                           headers=headers)

    assert respuesta.status_code == 422


def test_borrar_objeto(client):
    headers = registrar_y_headers(client)
    creado = client.post("/objetos", json={"title": "tarea"}, headers=headers).json()

    respuesta = client.delete(f"/objetos/{creado['id']}", headers=headers)

    assert respuesta.status_code == 204
    # y ya no aparece al listar
    assert client.get("/objetos", headers=headers).json() == []


def test_borrar_objeto_inexistente(client):
    headers = registrar_y_headers(client)

    respuesta = client.delete(f"/objetos/999", headers=headers)

    assert respuesta.status_code == 404
    assert "no existe" in respuesta.json()["detail"].lower()


# ---------- Seguridad: aislamiento entre usuarios ----------

def test_un_usuario_no_ve_objetos_de_otro(client):
    headers_ana = registrar_y_headers(client, "ana", "12345678")
    headers_bob = registrar_y_headers(client, "bob", "12345678")

    # ana crea un objeto
    client.post("/objetos", json={"title": "secreto de ana"}, headers=headers_ana)

    # bob lista los suyos: no debe ver nada de ana
    respuesta = client.get("/objetos", headers=headers_bob)

    assert respuesta.json() == []


def test_un_usuario_no_puede_borrar_objeto_de_otro(client):
    headers_ana = registrar_y_headers(client, "ana", "12345678")
    headers_bob = registrar_y_headers(client, "bob", "12345678")

    objeto_ana = client.post("/objetos", json={"title": "de ana"}, headers=headers_ana).json()

    # bob intenta borrar el objeto de ana
    respuesta = client.delete(f"/objetos/{objeto_ana['id']}", headers=headers_bob)

    assert respuesta.status_code == 404
    assert "no existe" in respuesta.json()["detail"].lower()

    # y el objeto de ana sigue vivo
    assert len(client.get("/objetos", headers=headers_ana).json()) == 1
