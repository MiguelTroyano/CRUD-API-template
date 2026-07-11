from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pwdlib import PasswordHash
from sqlmodel import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import engine
from models import Usuario

security = HTTPBearer()                                 # FastAPI espera un token en los headers.

password_hash = PasswordHash.recommended()
"""
Hasher: Argon2 con parámetros por defecto.
Usa "datos" distintos para cada usuario que permiten repetir contraseñas.
Usa algoritmos lentos de hashing para impedir ataques de fuerza bruta.
"""



"""
Importante que la API no acepte directamente la clase que define las tablas de la BBDD.
Esto permite a los usuarios controlar cosas que no interesa que controlen (como el id de su usuario o sus objetos, 
o el hash de su contraseña), para evitar errores inesperados o posibles ataques.
Si el atacante conoce el output del hash de tu contraseña, podría mandarla como tal. Ahora forzamos a que conozca
la contraseña original.
"""


#Función de autorización que se ejecutará antes que todos los endpoints en los que esté como argumento esta función
def dependencia_autorizacion(
        credenciales: HTTPAuthorizationCredentials = Depends(security)
) -> Usuario:
    #Obtener un token por headers
    token = credenciales.credentials

    #Error único para token sin propietario o propietario no registrado, firma o fecha de caducidad inválidas.
    no_autorizado = HTTPException(status_code= 401, detail= "Acceso denegado")

    #Obtener el id del usuario propietario del token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])         # si la firma es inválida o ha caducado lanza InvalidTokenError

        user_id = payload.get("sub")
        if user_id is None:
            raise no_autorizado         # token sin propietario
        
    except jwt.InvalidTokenError:
        raise no_autorizado

    #Obtener los datos del usuario
    with Session(engine) as session:
        usuario = session.get(Usuario, int(user_id))        # se usa .get(Tabla, id) para buscar una fila por clave primaria

        if usuario is None:
            raise no_autorizado     # usuario no registrado
        return usuario


def crear_token(usuario_id: int):
        expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(usuario_id), "exp": expira}
        return jwt.encode(payload= payload, key= SECRET_KEY, algorithm= ALGORITHM)