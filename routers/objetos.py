from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

from auth import dependencia_autorizacion
from database import get_session
from models import Usuario, Objeto
from schemas import ObjetoCrear, ObjetoLeer, ObjetoActualizar

router = APIRouter(prefix="/objetos", tags=["objetos"])
# prefix: todas las rutas de este router cuelgan de /objetos,
# por eso abajo se escribe "" en vez de "/objetos".
# tags: agrupación en /docs

#Ruta /objetos: post para crear 1, get para obtenerlos todos (en forma de lista de JSON)
@router.post("", response_model=ObjetoLeer, status_code=status.HTTP_201_CREATED)        # equivalente a hacer status_code=201 (legibilidad)
def crear_objeto(datos: ObjetoCrear,
                 session: Session = Depends(get_session),
                 usuario: Usuario = Depends(dependencia_autorizacion)):
    objeto = Objeto(
        title = datos.title,
        usuario_id = usuario.id
        # id se autogenera por SQL, y done usa su default (False)
    )

    session.add(objeto)         #objeto en estado TRANSITORIO, método add para añadir a la BBDD (ejec. INSERT)
    session.commit()
    session.refresh(objeto)
    return objeto

"""
Especificar el código de estado 201 (y 204 para eliminar) ayuda a cualquier persona/programa que haga peticiones 
a la API a entender lo que acaba de hacer.
"""

@router.get("", response_model=list[ObjetoLeer])
def listar_objetos(
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(dependencia_autorizacion)
):
    return session.exec(select(Objeto).where(Objeto.usuario_id == usuario.id)).all()       # devolverá una lista de objetos, que FastAPI convertirá a JSON automáticamente
"""
La anterior línea se podría haber reemplazado por el uso de Relationship de SQLModel, que permite 
listar de forma más clara y concisa las filas de clave foránea-primaria común.
"""


#Obtener 1 solo objeto: ruta /objetos/{id}. PUT para modificar, DELETE para eliminar.

"""
El método PUT en API RESTs, convencionalmente, sirve para actualizar un objeto entero, es decir,
colocar un objeto nuevo donde antes había otro. En este caso, sólo cambiamos 1 atributo del objeto,
por lo que el método PATCH sería más correcto. Sin embargo, ambos métodos valen, y como PUT es más 
polivalente, usaremos PUT.
"""
@router.put("/{id_objeto}", response_model=ObjetoLeer)
def actualizar_objeto(id_objeto: int, 
                    datos: ObjetoActualizar,
                    session: Session = Depends(get_session),
                    usuario: Usuario = Depends(dependencia_autorizacion)):
    """
    Modifica los campos especificados de un objeto.
    """
    objeto = session.get(Objeto, id_objeto)         #se usa .get(Tabla, id) para buscar una fila por clave primaria

    #Manejo de errores, necesario antes de modificar
    if not objeto or objeto.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail=F"Objeto de id {id_objeto} no encontrado")      #se lanza no encontrado si el objeto existe pero es de otro usuario.

    # Comportamiento de PATCH: Filtrar por argumentos especificados (en PUT se especifican todos)
    datos = datos.model_dump(exclude_unset=True)        # transforma el JSON en diccionario, eliminando los campos no especificados
    for campo, valor in datos.items():
        setattr(objeto, campo, valor)           # (tenemos el campo en forma de string, asi que lo conveniente es usar setattr)
    
    session.commit()
    session.refresh(objeto)
    return objeto


@router.delete("/{id_objeto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_objeto(id_objeto: int,
                    session: Session = Depends(get_session),
                    usuario: Usuario = Depends(dependencia_autorizacion)):
    objeto = session.get(Objeto, id_objeto)

    if not objeto or objeto.usuario_id != usuario.id:
        raise HTTPException(404, detail=F"No se pudo eliminar el objeto de id {id_objeto} porque no existe")
    
    session.delete(objeto)
    session.commit()
    
    return None         # un 204 no lleva cuerpo