from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import create_tables
from routers import users, items

# Database creation
create_tables()

#API creation
app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)


#FRONT-END
"""
In this case, since we only use HTML + JS (no React), we can host the front-end and the back-end in the
'same place'. Otherwise, we would need CORS (Cross-Origin Resource Sharing) so that both ends could talk to each other.
"""
app.mount("/static", StaticFiles(directory="static"), name="static")        #when the HTML is rendered, the CSS and JS are fetched through the API.

@app.get("/")
def home():
    return FileResponse("static/index.html")
