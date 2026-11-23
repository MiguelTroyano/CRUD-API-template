from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import create_tables
from routers import users, items

# Creación de la base de datos
create_tables()

#Creación de la API
app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)


#FRONT-END
"""
En este caso, como vamos a usar sólo HTML + JS (prescindimos de React), podemos alojar el front-end y el back-end
en el 'mismo sitio'. Si no, tendríamos que emplear CORS (Cross-Origin Resource Sharing) para poder comunicar ambos ends.
"""
app.mount("/static", StaticFiles(directory="static"), name="static")        #al renderizar el HTML, se pasa por la API para acceder a los CSS y el JS.

@app.get("/")
def home():
    return FileResponse("static/index.html")
