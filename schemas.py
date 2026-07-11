from models import UsuarioBase, ObjetoBase

class ObjetoCrear(ObjetoBase):
    """
    Clase con la información que aporta el usuario sobre un nuevo objeto.
    """
    pass                                                #(mismos atributos que el ObjetoBase)


class UsuarioCrear(UsuarioBase):       #Clase que se le pasa a la API: Solo con la info que obtenemos del usuario
    """
    Clase con la información que aporta el usuario sobre su nuevo usuario.
    """
    password: str