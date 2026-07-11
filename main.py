from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import crear_tablas
from routers import usuarios, objetos

# Creación de la base de datos
crear_tablas()

#Creación de la API
app = FastAPI()

app.include_router(usuarios.router)
app.include_router(objetos.router)


#FRONT-END
"""
En este caso, como vamos a usar sólo HTML + JS (prescindimos de React), podemos alojar el front-end y el back-end
en el 'mismo sitio'. Si no, tendríamos que emplear CORS (Cross-Origin Resource Sharing) para poder comunicar ambos ends.
"""
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")