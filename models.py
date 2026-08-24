from sqlmodel import SQLModel, Field
from pydantic import field_validator

# -- Objeto ---
class ObjetoBase(SQLModel):
    """
    Define el título como atributo base, OBLIGATORIO y DE +1 CARACTER (no todas las clases van a usar esta base).
    """
    title: str = Field(min_length=1, max_length=100)        # min_length protege ante títulos vacíos, aunque no de títulos únicamente compuestos por espacios ("  ")

    """
    Es NECESARIO marcar el título como obligatorio (no tipificado como None), ya que la clase que definirá la tabla 
    de SQL hereda esta clase.
    Esto provoca que la columna de la tabla esté tipificada como "NOT NULL"; lo cual protege a la base de datos de 
    inserciones corruptas realizadas desde cualquier otro sitio que no sean los endpoints de la API.
    """

    # filtro de los campos de entrada a la BBDD y de búsqueda (no se aplican a las lecturas)
    @field_validator("title", mode="before")      # mode="before": ejecuta los cambios antes de pasar por el resto de restricciones en Field
    @classmethod
    def limpiar_title(cls, v):
        """
        En caso de que se haya especificado un string, le quita los espacios del principio y el final.
        """
        if isinstance(v, str):
            return v.strip()
        return v
    """
    Se podría marcar mode="after" y, manualmente, verificar que haya quedado más de 1 letra y lanzar (en caso contrario) 
    un ValueError para simular el mismo rechazo de la petición.
    """

class Objeto(ObjetoBase, table=True):
    """
    Clase que define los atributos que van en la tabla de la BBDD
    """
    id: int = Field(default = None, primary_key=True)       # atributos con un default marcados no se hacen obligatorios DE ESPECIFICAR por Pydantic.
    done: bool = False                                      # para marcar atributos opcionales para la BBDD se deben tipificar como posible None.
    usuario_id: int = Field(foreign_key= "usuario.id")



# --- Usuario ---

# Para mantener un estilo de código reutilizable, se pueden definir las funciones de validación fuera de la clase.
def normalizar_username(v):
    if isinstance(v, str):
        return v.strip().lower()        #interesa normalizar todos los usuarios introducidos a minusculas para evitar incoherencias y confusiones
    return v

class UsuarioBase(SQLModel):
    """
    Define el nombre de usuario como atributo ÚNICO e indexado.
    """
    username: str = Field(unique = True, index=True, min_length=3, max_length=128, schema_extra={"pattern": r"^[a-zA-Z0-9_]+$"})
    """
    - max_length sirve tanto para validar peticiones como para definir el tipo de columna en la 
        BBDD (VARCHAR(max_length))

    - Se exige que los nombres de usuario estén compuestos únicamente por letras, números, y guiones bajos.
        Esto evita que se consideren como usuarios distintos dos con un espacio o emoji como única diferencia ("ana" y "a na").
        Restricción aplicada únicamente a la API, no a la BBDD.
    """

    @field_validator("username", mode="before")
    @classmethod
    def _normalizar(cls, v):
        return normalizar_username(v)
    """
    Apunte: existen vulnerabilidades como la letra "a" cirílica que es igual a la "a" normal pero que son
    consideradas distintas.
    """

class Usuario(UsuarioBase, table=True):
    id: int = Field(default = None, primary_key=True)
    hashed_password: str