from models import UsuarioBase, ObjetoBase
from sqlmodel import SQLModel

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
    title: str | None = None
    done: bool | None = None
    """
    No podemos usar la base para heredar el título, ya que en ella está marcada como obligatorio, y en actualizaciones
    parciales se puede no especificar.
    """


class UsuarioCrear(UsuarioBase):
    """
    Clase con la información que aporta el usuario sobre su nuevo usuario.
    """
    password: str


class UsuarioLeer(UsuarioBase):
    """
    Clase con la información que devolverá la API sobre los usuarios tratados
    """
    pass        # username (heredado) es lo único que el front necesita hoy. El id se incluirá cuando se necesite.