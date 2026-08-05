from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from auth import dependencia_autorizacion
from database import get_session
from models import Usuario, Objeto
from schemas import ObjetoCrear, ObjetoLeer

router = APIRouter(prefix="/objetos", tags=["objetos"])
# prefix: todas las rutas de este router cuelgan de /objetos,
# por eso abajo se escribe "" en vez de "/objetos".
# tags: agrupación en /docs

#Ruta /objetos: post para crear 1, get para obtenerlos todos (en forma de lista de JSON)
@router.post("", response_model=ObjetoLeer)
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
@router.put("/{id_objeto}", response_model=ObjetoLeer)
def actualizar_done(id_objeto: int, done: bool,        #ideal: obtener los argumentos de todas las funciones como JSON o por argumentos sueltos, no variar.
                    session: Session = Depends(get_session),
                    usuario: Usuario = Depends(dependencia_autorizacion)):
    objeto = session.get(Objeto, id_objeto)         #se usa .get(Tabla, id) para buscar una fila por clave primaria

    #Manejo de errores, necesario antes de modificar
    if not objeto or objeto.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail=F"Objeto de id {id_objeto} no encontrado")      #se lanza no encontrado si el objeto existe pero es de otro usuario.
    
    objeto.done = done

    #session.add(objeto)
    """
    Se puede poner la anterior línea, pero no es necesario. 
    Una instancia de Objeto puede estar en estado
    TRANSITORIO si se ha creado de la nada y no está conectado a la BBDD (todavía)
    PERSISTENTE si se ha obtenido directamente de la BBDD. En este caso el ORM SQLModel monitorea los cambios
        que se hagan a ese objeto en memoria y se trasladan a la BBDD en el próximo commit.
    """
    
    session.commit()
    session.refresh(objeto)
    return objeto


@router.delete("/{id_objeto}")
def eliminar_objeto(id_objeto: int,
                    session: Session = Depends(get_session),
                    usuario: Usuario = Depends(dependencia_autorizacion)):
    objeto = session.get(Objeto, id_objeto)

    if not objeto or objeto.usuario_id != usuario.id:
        raise HTTPException(404, detail=F"No se pudo eliminar el objeto de id {id_objeto} porque no existe")
    
    session.delete(objeto)
    session.commit()
    
    return {"ok": True}