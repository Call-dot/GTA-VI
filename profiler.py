# JSON save architecture suggested by AI + the internet, polished and customized by human hands

# Global persistent player data — settings, respect points, and unlocked cars.
# Stored as a single JSON file (PROFILE_PATH) separate from per-run saves.
#
# Structure:
#   _magic        – validity flag
#   respect       – total stars accumulated across all won runs
#   unlocked_cars – list of car asset keys the player owns
#   settings:
#     volume      – float 0..1   music volume
#     fullscreen  – bool         window mode at last exit

import json
import os
import pygame
from settings import CAR_MODELS

PROFILE_PATH  = "saves/profile.json"
PROFILE_MAGIC = "GTA6_PROFILE_V1"

# The first car is free
STARTER_CARS = ["red_car", "babyblue_car"]

# Price in respect-stars for each car.  Cars not listed default to free.
CAR_PRICES: dict[str, int] = {
    "red_car":       0,
    "pink_car":      3,
    "babyblue_car":  0,
    "camo_car":      8,
    "darkblue_car":  10,
    "name_car":      15,
    "orange_car":    12,
    "black_car":     20,
    "lime_car":      18,
}

_DEFAULTS: dict = {
    "_magic":        PROFILE_MAGIC,
    "respect":       0,
    "unlocked_cars": STARTER_CARS,
    "settings": {
        "volume":          0.5,
        "fullscreen":      False,
        "show_hitboxes":   False,
        "british_driving": False,
    },
}


def _ensure_dir():
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)


def load_profile() -> dict:
    """Load profile from disk, falling back to defaults on any error."""
    _ensure_dir()
    if not os.path.exists(PROFILE_PATH):
        return _deep_copy_defaults()
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _deep_copy_defaults()

    if data.get("_magic") != PROFILE_MAGIC:
        return _deep_copy_defaults()

    profile = _deep_copy_defaults()
    profile["respect"]       = int(data.get("respect", 0))
    profile["unlocked_cars"] = list(data.get("unlocked_cars", [STARTER_CARS]))
    s = data.get("settings", {})
    profile["settings"]["volume"]          = float(s.get("volume",          0.5))
    profile["settings"]["fullscreen"]      = bool(s.get("fullscreen",        False))
    profile["settings"]["show_hitboxes"]   = bool(s.get("show_hitboxes",     False))
    profile["settings"]["british_driving"] = bool(s.get("british_driving",   False))

    if STARTER_CARS not in profile["unlocked_cars"]:
        profile["unlocked_cars"].insert(0, STARTER_CARS)

    return profile


def save_profile(profile: dict):
    _ensure_dir()
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)


def _deep_copy_defaults() -> dict:
    import copy
    return copy.deepcopy(_DEFAULTS)


def award_respect(profile: dict, stars: int):
    """Add stars to total and persist.  Only call when mission is passed."""
    if stars > 0:
        profile["respect"] += stars
        save_profile(profile)


def try_purchase(profile: dict, car_key: str) -> str:
    """
    Attempt to purchase car_key.
    """
    if car_key in profile["unlocked_cars"]:
        return "already_owned"
    price = CAR_PRICES.get(car_key, 0)
    if profile["respect"] < price:
        return "insufficient"
    profile["respect"] -= price
    profile["unlocked_cars"].append(car_key)
    save_profile(profile)
    return "ok"


def apply_settings(profile: dict, game):
    """Apply stored settings to the live game instance."""
    s = profile["settings"]
    pygame.mixer.music.set_volume(s["volume"])

    # fullscreen
    if s["fullscreen"] and not getattr(game, "is_fullscreen", False):
        info = pygame.display.Info()
        game.screen = pygame.display.set_mode(
            (info.current_w, info.current_h),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,
        )
        game.is_fullscreen = True
    elif not s["fullscreen"] and getattr(game, "is_fullscreen", False):
        from settings import WIDTH, HEIGHT
        game.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        game.is_fullscreen = False

    # simple boolean flags — live on the game object so the rest of the code
    # can read them without importing profile
    game.show_hitboxes   = s["show_hitboxes"]
    game.british_driving = s["british_driving"]


def save_settings(profile: dict, game):
    """Snapshot current game settings into profile and persist."""
    profile["settings"]["volume"]          = pygame.mixer.music.get_volume()
    profile["settings"]["fullscreen"]      = getattr(game, "is_fullscreen",   False)
    profile["settings"]["show_hitboxes"]   = getattr(game, "show_hitboxes",   False)
    profile["settings"]["british_driving"] = getattr(game, "british_driving", False)
    save_profile(profile)