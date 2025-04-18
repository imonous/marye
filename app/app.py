from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

from app.lib.youtube import YouTube


load_dotenv()
yt_key = os.getenv("YOUTUBE_API")
client = httpx.AsyncClient()
yt = YouTube(yt_key, client)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await yt.close()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    result = await yt.search(q)
    return templates.TemplateResponse(
        request=request, 
        name="search.html",  
        context={"videos": result.items}
    )