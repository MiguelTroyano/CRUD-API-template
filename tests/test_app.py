from conftest import register_and_get_headers
from sqlmodel import select
from models import User


# ---------- Registration and login ----------

def test_register_returns_username(client):
    response = client.post("/register", json={"username": "ana", "password": "12345678"})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "ana"
    assert "hashed_password" not in data
    assert "password" not in data


def test_register_duplicate_username_fails(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    response = client.post("/register", json={"username": "ana", "password": "other123"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"


def test_register_short_password_fails(client, session):
    response = client.post("/register", json={"username": "ana", "password": "five"})

    assert response.status_code == 422
    assert session.exec(select(User).where(User.username == "ana")).first() is None

def test_register_short_username_fails(client):
    response = client.post("/register", json={"username": "ab", "password": "12345678"})
    assert response.status_code == 422


def test_login_success_returns_token(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    response = client.post("/login", json={"username": "ana", "password": "12345678"})

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_returns_401(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})

    response = client.post("/login", json={"username": "ana", "password": "WRONG123"})

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_unknown_user_returns_401(client):
    response = client.post("/login", json={"username": "ghost", "password": "12345678"})

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert response.json()["detail"] == "Incorrect username or password"


def test_username_is_normalized_to_lowercase(client):
    client.post("/register", json={"username": "Ana", "password": "12345678"})
    response = client.post("/login", json={"username": "ANA", "password": "12345678"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_duplicate_username_is_case_insensitive(client):
    client.post("/register", json={"username": "ana", "password": "12345678"})
    response = client.post("/register", json={"username": "Ana", "password": "other123"})
    assert response.status_code == 400


def test_login_short_password_returns_401_not_422(client):
    client.post("/register", json={"username": "ana", "password": "correct123"})
    response = client.post("/login", json={"username": "ana", "password": "no"})
    assert response.status_code == 401       # login does not apply the registration length rules

# ---------- Authorization ----------

def test_list_items_without_token_returns_401(client):
    response = client.get("/items")

    assert response.status_code == 401


# ---------- Item CRUD ----------

def test_create_item_assigns_it_to_user(client):
    headers = register_and_get_headers(client)

    response = client.post("/items", json={"title": "bread"}, headers=headers)

    assert response.status_code == 201
    item = response.json()
    assert item["title"] == "bread"
    assert item["done"] is False


def test_create_item_empty_title_fails(client):
    headers = register_and_get_headers(client)
    response = client.post("/items", json={"title": ""}, headers=headers)
    assert response.status_code == 422


def test_create_item_whitespace_only_fails(client):
    headers = register_and_get_headers(client)
    response = client.post("/items", json={"title": "   "}, headers=headers)
    assert response.status_code == 422


def test_create_item_strips_whitespace(client):
    headers = register_and_get_headers(client)
    response = client.post("/items", json={"title": "  with spaces  "}, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "with spaces"


def test_list_returns_created_items(client):
    headers = register_and_get_headers(client)
    client.post("/items", json={"title": "item 1"}, headers=headers)
    client.post("/items", json={"title": "item 2"}, headers=headers)

    response = client.get("/items", headers=headers)

    assert response.status_code == 200
    items = [(i["title"], i["done"]) for i in response.json()]
    assert items == [("item 1", False), ("item 2", False)]


def test_mark_done(client):
    headers = register_and_get_headers(client)
    created = client.post("/items", json={"title": "task"}, headers=headers).json()

    response = client.put(f"/items/{created['id']}", json={"done": True}, headers=headers)

    assert response.status_code == 200
    assert response.json()["done"] is True


def test_update_title_too_long_fails(client):
    headers = register_and_get_headers(client)
    created = client.post("/items", json={"title": "item"}, headers=headers).json()

    response = client.put(f"/items/{created['id']}",
                          json={"title": "x" * 200},
                          headers=headers)

    assert response.status_code == 422


def test_delete_item(client):
    headers = register_and_get_headers(client)
    created = client.post("/items", json={"title": "task"}, headers=headers).json()

    response = client.delete(f"/items/{created['id']}", headers=headers)

    assert response.status_code == 204
    assert client.get("/items", headers=headers).json() == []


def test_delete_nonexistent_item(client):
    headers = register_and_get_headers(client)

    response = client.delete(f"/items/999", headers=headers)

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"].lower()


# ---------- User isolation ----------

def test_user_cannot_see_other_users_items(client):
    headers_ana = register_and_get_headers(client, "ana", "12345678")
    headers_bob = register_and_get_headers(client, "bob", "12345678")

    client.post("/items", json={"title": "ana's secret"}, headers=headers_ana)

    response = client.get("/items", headers=headers_bob)

    assert response.json() == []


def test_user_cannot_delete_other_users_item(client):
    headers_ana = register_and_get_headers(client, "ana", "12345678")
    headers_bob = register_and_get_headers(client, "bob", "12345678")

    ana_item = client.post("/items", json={"title": "ana's item"}, headers=headers_ana).json()

    response = client.delete(f"/items/{ana_item['id']}", headers=headers_bob)

    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"].lower()

    assert len(client.get("/items", headers=headers_ana).json()) == 1
