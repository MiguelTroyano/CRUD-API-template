from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import create_tables
from routers import users, items

create_tables()

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)


# The front-end is served by the API itself, so no CORS configuration is needed.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return FileResponse("static/index.html")
