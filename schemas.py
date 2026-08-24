from models import UsuarioBase, ObjetoBase, normalizar_username
from sqlmodel import SQLModel, Field
from pydantic import field_validator

class ObjetoCrear(ObjetoBase):
    """
    Clase con la información que aporta el usuario sobre un nuevo objeto.
    """
    pass                                                #(mismos atributos que el ObjetoBase (title))


class ObjetoLeer(ObjetoBase):
    """
    Clase con la información que devolverá la API sobre los objetos tratados
    """
    id: int         # necesario para poder enviar desde el front-end peticiones de operaciones PUT y DELETE
    done: bool      # necesario para la operación PUT
    """
    El usuario_id no es necesario para ninguna operación (lo deduce el back-end con el token que envía la petición). 
    Entonces, aunque no suponga ninguna amenaza incluirlo, al no ser necesario, es mejor no hacerlo.
    Igualmente, si añadiésemos otra operación en la que fuese necesario que el front-end conociese la identidad del 
    dueño del objeto de antemano, tendríamos que incluirlo.
    """


class ObjetoActualizar(SQLModel):
    """
    Clase con la posible información que puede proveer un usuario para modificar un objeto.
    """
    title: str | None = Field(default=None, min_length=1, max_length=100)
    done: bool | None = None
    """
    No podemos usar la base para heredar el título, ya que en ella está marcada como obligatorio, y en actualizaciones
    parciales se puede no especificar.
    """

    @field_validator("title", mode="before")      # mode="before": ejecuta los cambios antes de pasar por el resto de restricciones en Field
    @classmethod
    def limpiar_title(cls, v):
        """
        En caso de que se haya especificado un string, le quita los espacios del principio y el final.
        """
        if isinstance(v, str):
            return v.strip()
        return v


class UsuarioRegistrar(UsuarioBase):
    """
    Clase con la información que aporta el usuario sobre su nuevo usuario.
    """
    password: str = Field(min_length=8, max_length=128)         # cualquier POST que se haga con una contraseña de <8 letras lanzará 422 (código de error para formato de peticiones erróneos).


class UsuarioLogin(SQLModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    """
    A la hora de iniciar sesión, la única restricción que se debe imponer a la contraseña introducida es aquella que 
    SIEMPRE se va a imponer a la recién creada.
    Quizá, el mínimo número de letras de las contraseñas en el futuro pasa a ser de 8 a 12. Entonces, Login y Registro
    no pueden compartir la misma restricción, ya que el Login quedaría deprecado para aquellos usuarios que se registraron
    bajo las anteriores restricciones.

    Además, que salte el mismo error al iniciar sesión que al registrarse, implica que a quién esté inciando sesión se le 
    podría dar información relevante únicamente en el momento de crear (restricciones de creación).
    """

    @field_validator("username", mode="before")
    @classmethod
    def _normalizar(cls, v):
        return normalizar_username(v)


class UsuarioLeer(UsuarioBase):
    """
    Clase con la información que devolverá la API sobre los usuarios tratados
    """
    pass        # username (heredado) es lo único que el front necesita hoy. El id se incluirá cuando se necesite.