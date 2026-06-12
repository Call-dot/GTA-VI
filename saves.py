# AI helped with creating the architecture for the JSON / tkinter file management 

# saves.py
# Handles serialising / deserialising completed run records to/from disk.
#
# A save record stores:
#   seed        – int   – the RNG seed the run used
#   igt         – float – final in-game time (seconds since midnight-offset)
#   health      – int   – remaining stars at end of run
#   car_model   – str   – asset key for the car that was driven
#   success     – bool  – True = mission passed
#   tiles       – list[str]  – the full row-layout list (enables replay)
#   tile_data   – list[dict] – the full structural tile-data list (enables replay)
#   endpoint    – int | None – playerpos value that ended the run
#
# Files are stored as JSON, one record per file, inside SAVES_DIR.
# The filename is <seed>_<unix-timestamp-ms>.json so every run is unique.

import json
import os
import time
import tkinter as tk
from tkinter import filedialog

SAVES_DIR  = "saves/runs"        # relative to the working directory; created on first write
SAVE_MAGIC = "GTA6_SAVE_V1"  # written into every save; checked on import


# ── public helpers ───────────────────────────────────────────────────────────

def ensure_saves_dir():
    os.makedirs(SAVES_DIR, exist_ok=True)


def save_run(game) -> str:
    """
    Serialise the current completed run from *game* and write it to disk.
    Returns the full path of the written file.
    """
    ensure_saves_dir()
    ts  = int(time.time() * 1000)
    filename = f"{game.seed}_{ts}.json"
    path = os.path.join(SAVES_DIR, filename)

    record = {
        "_magic":     SAVE_MAGIC,
        "seed":       game.seed,
        "igt":        game.igt,
        "health":     game.health,
        "car_model":  game.player_model or "",
        "success":    game.success,
        "tiles":      game.tiles,
        "tile_data":  game.tile_data,
        "endpoint":   game.endpoint,
        "saved_at":   ts,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, separators=(",", ":"))

    return path


def load_all_saves() -> list[dict]:
    """
    Read every *.json file in SAVES_DIR and return them as a sorted list.
    Sort order: health DESC → igt ASC → seed ASC.
    Each dict has all the keys written by save_run().
    """
    ensure_saves_dir()
    records = []
    for fname in os.listdir(SAVES_DIR):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(SAVES_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                rec = json.load(f)
            rec["_path"] = path   # stash for later (export, delete, etc.)
            records.append(rec)
        except (json.JSONDecodeError, OSError):
            continue   # silently skip corrupt files

    records.sort(key=lambda r: (-r.get("health", 0),
                                 r.get("igt", 0),
                                 r.get("seed", 0)))
    return records


def delete_save(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


# ── import / export via OS file dialog ──────────────────────────────────────

def _hide_tk_root():
    root = tk.Tk()
    root.withdraw()
    return root


def export_save(path: str):
    """
    Open a Save-As dialog so the user can copy a save file to wherever they like.
    *path* is the source path returned by save_run() or stored in a record's '_path'.
    """
    root = _hide_tk_root()
    dest = filedialog.asksaveasfilename(
        title="Export save file",
        defaultextension=".json",
        filetypes=[("Save files", "*.json"), ("All files", "*.*")],
        initialfile=os.path.basename(path),
    )
    root.destroy()
    if not dest:
        return False   # user cancelled

    with open(path, "r", encoding="utf-8") as src_f:
        data = src_f.read()
    with open(dest, "w", encoding="utf-8") as dst_f:
        dst_f.write(data)
    return True


def import_save() -> dict | None:
    """
    Open a file-picker so the user can choose a save JSON from anywhere on disk.
    Copies it into SAVES_DIR and returns the parsed record, or None on cancel/error.
    """
    root = _hide_tk_root()
    src = filedialog.askopenfilename(
        title="Import save file",
        filetypes=[("Save files", "*.json"), ("All files", "*.*")],
    )
    root.destroy()
    if not src:
        return None

    try:
        with open(src, "r", encoding="utf-8") as f:
            record = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    if record.get("_magic") != SAVE_MAGIC:
        return None  # not a valid GTA6 save file

    ensure_saves_dir()
    ts   = int(time.time() * 1000)
    seed = record.get("seed", "unknown")
    dest = os.path.join(SAVES_DIR, f"{seed}_{ts}.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(record, f, separators=(",", ":"))

    record["_path"] = dest
    return record


def format_gametime(igt: float, departure: int = 0) -> str:
    """Convert raw IGT seconds + departure offset to HH:MM:SS string."""
    total   = int(igt) + departure
    mm, ss  = divmod(total, 60)
    hh, mm  = divmod(mm, 60)
    return f"{hh}:{mm:02d}:{ss:02d}"