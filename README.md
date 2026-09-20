Using FastAPI with SQLModel.

The back-end follows a structured approach designed to serve as a template for other projects.
The front-end, in contrast, is specifically tailored to display database content in a specialized manner.

User management using pwdlib: registration and login. Hashing: Argon2. Authentication tokens: JWT.

Token protection is highly vulnerable (stored in JS `localStorage`). Future update: use of HttpOnly cookies to handle tokens.

No CORS system is implemented.

---


**Files:**

`database.py`: creation of the database engine and session generator.

`models.py`: classes defining base models and database table models for users and objects.

`schemas.py`: classes defining the models used by endpoints for their operations.

`auth.py`: functions for token verification and creation.

`config.py`: retrieval of configuration parameters.

`routers/objetos.py`: endpoints for CRUD operations on objects.

`routers/usuarios.py`: endpoints for registration and login.

`static`: folder containing the entire front-end.
