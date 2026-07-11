from sqlmodel import SQLModel, Field

# -- Objeto ---
class ObjetoBase(SQLModel):
    title: str                                          # title: atributo que comparten el resto de clases

class Objeto(ObjetoBase, table=True):
    """
    Clase que define los atributos que van en la tabla de la BBDD
    """
    id: int = Field(default = None, primary_key=True)
    done: bool = False
    usuario_id: int = Field(foreign_key= "usuario.id")



# --- Usuario ---
class UsuarioBase(SQLModel):
    username: str = Field(unique = True, index=True)

class Usuario(UsuarioBase, table=True):
    id: int = Field(default = None, primary_key=True)
    hashed_password: str