GTA‑VI Web Prototype (client-side)

This folder contains a minimal JavaScript/Canvas port of the game's core loop. It is intended as a prototype and is not a line-by-line port of the original Pygame code — instead it reproduces gameplay elements (tile generation, NPCs, collisions, powerups) so you can run the game in a browser.

How to preview locally

1. You can serve the `web/` folder with any static server. Example using Python 3:

   python -m http.server 8000 --directory web

2. Open http://127.0.0.1:8000 in your browser.

Controls

- W / ArrowUp: accelerate
- S / ArrowDown: brake/reverse
- A / ArrowLeft: steer left
- D / ArrowRight: steer right
- Q: use/steal powerup (not implemented in prototype)

Save format

The Export Save button downloads a JSON file compatible in shape with the project's `saves.save_run()` format. Some fields are simplified, but the keys (`seed`, `igt`, `health`, `car_model`, `tiles`, `tile_data`, `endpoint`, `saved_at`) match the original layout so server-side tools can consume the files.

Next steps to improve

- Port more of the original level & AI logic for parity
- Add proper assets (converted PNGs + fonts)
- Implement powerups fully and audio with Web Audio
- Add mobile input support and polish UI
