from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import pages, fragments, health
from .data.loader import load_dataset, get_dataset

app = FastAPI(title="Analytics Workbench")

app.include_router(health.router)
app.include_router(pages.router)
app.include_router(fragments.router)

@app.on_event("startup")
async def startup_event():
    get_dataset() # pre-load dataset
