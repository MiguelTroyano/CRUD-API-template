Uso de FastAPI con SQLModel.

Se ha intentado seguir una forma esquemática para formar el back-end, de modo que pueda servir como plantilla para cualquier otro proyecto. 
El front-end, por el contrario, está muy direccionado a mostrar el contenido de la BBDD de una forma más especializada.

Uso de clases limitada. Uso, por el contrario, de URLs formateadas, argumentos sueltos, y personalización de outputs e inputs manuales en cada función.

Gestión de usuarios con pwdlib: registro, login. Hashing: Argon2. Tokens de autenticación: JWT.

Protección de tokens muy vulnerable (almacenados en localStorage de JS).

No se usa ningún sistema CORS.
