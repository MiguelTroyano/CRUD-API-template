from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

from auth import get_current_user
from database import get_session
from models import User, Item
from schemas import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])
# prefix: todas las rutas de este router cuelgan de /items,
# por eso abajo se escribe "" en vez de "/items".
# tags: agrupación en /docs

#Ruta /items: post para crear 1, get para obtenerlos todos (en forma de lista de JSON)
@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)        # equivalente a hacer status_code=201 (legibilidad)
def create_item(data: ItemCreate,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    item = Item(
        title = data.title,
        user_id = user.id
        # id se autogenera por SQL, y done usa su default (False)
    )

    session.add(item)         #objeto en estado TRANSITORIO, método add para añadir a la BBDD (ejec. INSERT)
    session.commit()
    session.refresh(item)
    return item

"""
Especificar el código de estado 201 (y 204 para eliminar) ayuda a cualquier persona/programa que haga peticiones
a la API a entender lo que acaba de hacer.
"""

@router.get("", response_model=list[ItemRead])
def list_items(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    return session.exec(select(Item).where(Item.user_id == user.id)).all()       # devolverá una lista de objetos, que FastAPI convertirá a JSON automáticamente
"""
La anterior línea se podría haber reemplazado por el uso de Relationship de SQLModel, que permite
listar de forma más clara y concisa las filas de clave foránea-primaria común.
"""


#Obtener 1 solo objeto: ruta /items/{id}. PUT para modificar, DELETE para eliminar.

"""
El método PUT en API RESTs, convencionalmente, sirve para actualizar un objeto entero, es decir,
colocar un objeto nuevo donde antes había otro. En este caso, sólo cambiamos 1 atributo del objeto,
por lo que el método PATCH sería más correcto. Sin embargo, ambos métodos valen, y como PUT es más
polivalente, usaremos PUT.
"""
@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int,
                data: ItemUpdate,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    """
    Modifica los campos especificados de un objeto.
    """
    item = session.get(Item, item_id)         #se usa .get(Tabla, id) para buscar una fila por clave primaria

    #Manejo de errores, necesario antes de modificar
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")      #se lanza no encontrado si el objeto existe pero es de otro usuario.

    # Comportamiento de PATCH: Filtrar por argumentos especificados (en PUT se especifican todos)
    updates = data.model_dump(exclude_unset=True)        # transforma el JSON en diccionario, eliminando los campos no especificados
    for field, value in updates.items():
        setattr(item, field, value)           # (tenemos el campo en forma de string, asi que lo conveniente es usar setattr)

    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int,
                session: Session = Depends(get_session),
                user: User = Depends(get_current_user)):
    item = session.get(Item, item_id)

    if not item or item.user_id != user.id:
        raise HTTPException(404, detail=f"Could not delete item with id {item_id} because it does not exist")

    session.delete(item)
    session.commit()

    return None         # un 204 no lleva cuerpo
