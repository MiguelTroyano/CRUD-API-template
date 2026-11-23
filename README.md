<div align="center">

# Scalable CRUD API

REST API built with **FastAPI** and **SQLModel**, featuring user registration, JWT authentication and a lightweight HTML + JS front-end.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.138-009688?logo=fastapi&logoColor=white)
![SQLModel](https://img.shields.io/badge/SQLModel-SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)

</div>

---

## Table of contents

- [About](#about)
- [Features](#features)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [API usage](#api-usage)
- [Tests](#tests)
- [Project structure](#project-structure)
- [Known limitations](#known-limitations)

## About

The back-end follows a structured layout designed to serve as a **template** for other projects. The front-end, in contrast, is tailored specifically to display the database content.

Classes are kept to a minimum on purpose: the code relies on formatted URLs, plain arguments and inputs and outputs defined by hand in each endpoint.

## Features

- **Users**: registration and login with [pwdlib](https://github.com/frankie567/pwdlib). Passwords are stored as **Argon2** hashes.
- **Authentication**: **JWT** tokens with configurable expiration.
- **Item CRUD**: each user can only see and modify their own items.
- **Validation**: input constraints with Pydantic and specific HTTP status codes.
- **Built-in front-end**: served by the API itself, so no CORS is needed.
- **Docker**: ready-to-run image, with the database stored in a persistent volume.

## Quick start

### Option A: Docker

1. Create a `.env` file in the project root with the key used to sign tokens:

   ```env
   JWT_SECRET_KEY=put_a_long_random_key_here
   ```

   You can generate one with `python -c "import secrets; print(secrets.token_hex(32))"`.

2. Build and start the container:

   ```bash
   docker compose up -d --build
   ```

3. Open **http://localhost:8000**.

| Action | Command |
| --- | --- |
| Stop | `docker compose stop` |
| Resume | `docker compose start` |
| Remove the container (keeps the data) | `docker compose down` |
| Remove the container **and the data** | `docker compose down -v` |
| View logs | `docker compose logs -f` |

### Option B: locally with Python

```bash
pip install -r requirements.txt
cp config.ini.example config.ini   # then set your own secret_key
uvicorn main:app --reload
```

## Configuration

Each value is read from an **environment variable** first. If it is not set, it is taken from `config.ini`.

| Environment variable | `config.ini` key | Description | Example |
| --- | --- | --- | --- |
| `JWT_SECRET_KEY` | `secret_key` | Key used to sign tokens | `c9d1...e8a` |
| `JWT_ALGORITHM` | `algorithm` | Signing algorithm | `HS256` |
| `JWT_EXP_MINS` | `exp_mins` | Token lifetime in minutes | `30` |
| `DATABASE_URL` | — | Database connection string | `sqlite:///app.db` |

`config.ini.example` contains a template for `config.ini`.

## API usage

Interactive documentation (Swagger) is generated automatically at **http://localhost:8000/docs**.

### Endpoints

| Method | Path | Description | Auth |
| --- | --- | --- | :---: |
| `GET` | `/` | Front-end | — |
| `POST` | `/register` | Register a user | — |
| `POST` | `/login` | Log in and get a token | — |
| `GET` | `/items` | List the user's items | 🔒 |
| `POST` | `/items` | Create an item | 🔒 |
| `PUT` | `/items/{id}` | Update title and/or status | 🔒 |
| `DELETE` | `/items/{id}` | Delete an item | 🔒 |

🔒 Requires the `Authorization: Bearer <token>` header.

### Example flow

```bash
# 1. Register (username: 3-128 alphanumeric characters or "_"; password: at least 8)
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "jose", "password": "12345678"}'

# 2. Log in: returns {"access_token": "..."}
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "jose", "password": "12345678"}'

# 3. Create an item with the token you received
curl -X POST http://localhost:8000/items \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first item"}'
```

## Tests

Tests use an **in-memory** database, so they never touch `app.db`.

```bash
pip install -r requirements-dev.txt
pytest
```

## Project structure

```text
.
├── main.py              # Entry point: creates the app, registers routers and serves the front-end
├── config.py            # Configuration loading (environment variables / config.ini)
├── database.py          # Database engine and session generator
├── models.py            # Base models and table models (users and items)
├── schemas.py           # Endpoint input and output models
├── auth.py              # JWT token creation and verification
├── routers/
│   ├── users.py         # Registration and login
│   └── items.py         # CRUD operations on items
├── static/              # Front-end (HTML, CSS and JS)
├── tests/               # pytest tests
├── Dockerfile
└── compose.yaml
```

## Known limitations

This is a learning project. These points should be reviewed before using it in production:

- **Token storage**: the token is kept in JS `localStorage`, which makes it vulnerable to XSS attacks. Planned update: handle tokens with HttpOnly cookies.
- **No CORS**: not needed because the front-end is served by the API itself. It would have to be configured if they were split.
- **No migrations**: tables are created with `create_all`, so changing their structure requires recreating the database. The fix would be to use Alembic.
- **SQLite**: fine for development. PostgreSQL would be preferable in production: it only takes changing `DATABASE_URL` and installing its driver (`psycopg`).
