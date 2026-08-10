from sqlmodel import SQLModel, Field

# -- Objeto ---
class ObjetoBase(SQLModel):
    """
    Define el título como atributo base, OBLIGATORIO y DE +1 CARACTER (no todas las clases van a usar esta base).
    """
    title: str = Field(min_length=1)        # protege ante títulos vacíos, aunque no de títulos únicamente compuestos por espacios ("  ")

    """
    Es NECESARIO marcar el título como obligatorio, ya que la clase que definirá la tabla de SQL hereda esta clase.
    Esto provoca que la columna de la tabla esté tipificada como "NOT NULL"; lo cual protege a la base de datos de 
    inserciones corruptas realizadas desde cualquier otro sitio que no sean los endpoints de la API.
    """

class Objeto(ObjetoBase, table=True):
    """
    Clase que define los atributos que van en la tabla de la BBDD
    """
    id: int = Field(default = None, primary_key=True)       # atributos con un default marcados no se hacen obligatorios DE ESPECIFICAR por Pydantic
    done: bool = False
    usuario_id: int = Field(foreign_key= "usuario.id")



# --- Usuario ---
class UsuarioBase(SQLModel):
    """
    Define el nombre de usuario como atributo ÚNICO e indexado.
    """
    username: str = Field(unique = True, index=True)

class Usuario(UsuarioBase, table=True):
    id: int = Field(default = None, primary_key=True)
    hashed_password: str