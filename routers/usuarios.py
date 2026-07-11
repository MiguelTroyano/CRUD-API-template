from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

from auth import password_hash, crear_token
from database import engine
from models import Usuario
from schemas import UsuarioCrear

router = APIRouter(tags=["usuarios"])       # tags: agrupa estos endpoints en /docs
# Sin prefix: /register y /login no comparten raíz de URL.

#Ruta /register. Siempre se accede por un método POST, para crear un nuevo usuario.
@router.post("/register")
def crear_usuario(datos: UsuarioCrear):
    with Session(engine) as session:

        #Comprobar que no exista un usuario con el mismo nombre
        existe = session.exec(
            select(Usuario).where(Usuario.username == datos.username)
        ).first()
        if existe:
            raise HTTPException(status_code=400, detail="Nombre de usuario ya en uso")
        
        #Crear la instancia del usuario
        usuario = Usuario(
            username = datos.username,
            hashed_password= password_hash.hash(datos.password)         #Nunca guardamos la contraseña literal del usuario
        )

        #Actualizar la BBDD
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        return {"id": usuario.id, "username": usuario.username}         #Esto podría ser una clase UsuarioLeer
    

#Ruta /login. Método POST: se crea un token de acceso si los datos de acceso son válidos.
@router.post("/login")
def acceder(datos: UsuarioCrear):           #los atributos introducidos por el usuario para registrarse y acceder son los mismos
    with Session(engine) as session:

        #Comprobar que existe el usuario que está intentando iniciar sesión, y obtener su contraseña hasheada
        usuario = session.exec(
            select(Usuario).where(Usuario.username == datos.username)
        ).first()

        if not usuario or not password_hash.verify(datos.password, usuario.hashed_password):        #se lanza el mismo error por ambos motivos, para evitar conteo de usuarios
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        
        """
        Un token JWT contiene 3 segmentos: cabecera.contenido.firma
        La cabecera contiene el algoritmo usado.
        El contenido (payload) consta tanto del usuario (SUBject), como la fecha de EXPiración del token.
        Estas dos partes son accesibles para cualquiera. NO INCLUIR NUNCA INFORMACION CONFIDENCIAL EN ELLAS. No enviar el username como sub, ya que puede contener datos personales.
        La firma permite verificar la procedencia del token. El servidor la genera y verifica su validez a partir de la cabecera, el payload y una clave secreta del servidor.
        El token se lleva su propia prueba encima, entonces el servidor no guarda nada.
        No hay tabla de sesiones, no hay que consultar la base de datos para saber si un token es legítimo. Escala bien.

        El único riesgo es el posible robo de un token, que permite al ladrón usar el token a su gusto. Por eso se hacen fechas de expiración y se 
        usan tanto ellas como la identidad del usuario para construir la firma; para que si un atacante roba un token, que solo lo pueda usar un tiempo
        y que no pueda cambiar ni su identidad (a una administrativa) ni alargar su fecha de expiración (ya que la firma cambiaría).
        """
        token = crear_token(usuario.id)

        return {"access_token": token, "token_type": "bearer"}