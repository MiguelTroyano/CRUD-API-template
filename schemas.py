from models import UsuarioBase, ObjetoBase

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



class UsuarioCrear(UsuarioBase):       #Clase que se le pasa a la API: Solo con la info que obtenemos del usuario
    """
    Clase con la información que aporta el usuario sobre su nuevo usuario.
    """
    password: str


class UsuarioLeer(UsuarioBase):
    """
    Clase con la información que devolverá la API sobre los usuarios tratados
    """
    pass        # username (heredado) es lo único que el front necesita hoy. El id se incluirá cuando se necesite.