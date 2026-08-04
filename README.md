Uso de FastAPI con SQLModel.

Se ha intentado seguir una forma esquemática para formar el back-end, de modo que pueda servir como plantilla para cualquier otro proyecto. 
El front-end, por el contrario, está muy direccionado a mostrar el contenido de la BBDD de una forma más especializada.

Uso de clases limitada. Uso, por el contrario, de URLs formateadas, argumentos sueltos, y personalización de outputs e inputs manuales en cada función.

Gestión de usuarios con pwdlib: registro, login. Hashing: Argon2. Tokens de autenticación: JWT.

Protección de tokens muy vulnerable (almacenados en localStorage de JS).

No se usa ningún sistema CORS.

---


**Archivos:**

`database.py`: creación del motor de la BBDD y el generador de sesiones.

`models.py`: clases que definen los modelos base y los modelos tabla de los usuarios y los objetos.

`schemas.py`: clases que definen los modelos que obtienen los endpoints para sus funciones.

`auth.py`: funciones de verificación y creación de tokens.

`config.py`: obtención de parámetros de configuración.

`routers/objetos.py`: endpoints de operaciones CRUD sobre objetos.

`routers/usuarios.py`: endpoints de registro y log-in.

`static`: carpeta con todo el front-end