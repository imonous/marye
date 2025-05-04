from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

from app.config import load_config
from app.lib.llm import Validator
from app.lib.youtube import YouTube

load_dotenv()
yt_key = os.getenv("YOUTUBE_API")
or_key = os.getenv("OPENROUTER_API")

client = httpx.AsyncClient()
yt = YouTube(yt_key, client)
validator = Validator(or_key, client)

app_config = load_config()

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
        request=request, name="pages/index.html"
    )

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    result = await yt.search(q, app_config.show_shorts)
    return templates.TemplateResponse(
        request=request, 
        name="pages/search.html",  
        context={"videos": result.items}
    )

@app.get("/watch", response_class=HTMLResponse)
async def watch(request: Request, v: str):
    ctx = await yt.get_video_context(v)
    if not await validator.validate(ctx):
        return RedirectResponse(url="/watch/denied", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="pages/watch.html",
        context={"video_id": v}
    )

@app.get("/watch/denied", response_class=HTMLResponse)
async def watch_denied(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pages/watch_denied.html"
    )