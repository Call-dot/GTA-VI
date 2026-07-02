# Web-version README additions

This branch adds a small FastAPI web frontend that lets you browse saved runs (JSON files in saves/runs) and preview their tile layout in a canvas-based viewer.

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/ to view saves.

Next steps (full browser port):
- The repo contains the full Pygame implementation. Porting the live gameplay to the browser requires reimplementing the game loop and rendering in JS (Canvas/WebGL). The web app here is a first step — it exposes saves and provides a simple animated playback of tile layouts. 
