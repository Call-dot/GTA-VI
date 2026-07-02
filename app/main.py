from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pathlib
import json

# Import the project's save helpers
import saves

app = FastAPI(title="GTA-VI Web")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

SAVES_DIR = os.path.join("saves", "runs")


@app.get("/")
async def index(request: Request):
    records = saves.load_all_saves()
    # expose filenames (basename) so links are stable
    for r in records:
        r["_basename"] = os.path.basename(r.get("_path", ""))
    return templates.TemplateResponse("index.html", {"request": request, "records": records})


@app.get("/saves/{fname}")
async def view_save(request: Request, fname: str):
    records = saves.load_all_saves()
    record = None
    for r in records:
        if os.path.basename(r.get("_path", "")) == fname:
            record = r
            break
    if not record:
        raise HTTPException(status_code=404, detail="Save not found")
    return templates.TemplateResponse("save.html", {"request": request, "record": record, "basename": fname})


@app.get("/download/{fname}")
async def download(fname: str):
    # Very small safety check: file must live under SAVES_DIR
    path = os.path.join(SAVES_DIR, fname)
    path = os.path.normpath(path)
    if not path.startswith(os.path.normpath(SAVES_DIR)):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=fname)
