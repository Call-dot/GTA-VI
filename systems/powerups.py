# powerups.py
# Defines all powerup types and their spawn weights.
# To add a new powerup: add an entry to POWERUP_TYPES and include its key in POWERUP_WEIGHTS.

POWERUP_TYPES = {
    None: {
        "label": None,
        "color": None,           # tint color drawn on the trunk icon (R, G, B)
        "icon": None,            # asset key passed to assets.get_image(); None = no icon
    },
    "speed": {
        "label": "speed",
        "color": (255, 220, 50), # yellow
        "icon": "powerup_speed", # load this key from AssetLoader
    },
    "bomb": {
        "label": "bomb",
        "color": (255, 80, 80),  # red
        "icon": "powerup_bomb",
    },
}

# Relative spawn weights.  Higher = more common.
# Must include None (= no powerup carried).
POWERUP_WEIGHTS = {
    None:    70,   # ~70 % of NPCs carry nothing
    "speed": 18,   # ~18 % carry a speed boost
    "bomb":  12,   # ~12 % carry a bomb
}

# Radius (pixels) cleared by the bomb powerup
BOMB_RADIUS = 350

# How long the speed powerup lasts (seconds)
SPEED_POWERUP_DURATION = 8.0

# ── helpers ────────────────────────────────────────────────────────────────────

def weighted_random_powerup():
    """Return a powerup key (or None) sampled according to POWERUP_WEIGHTS."""
    import random
    keys    = list(POWERUP_WEIGHTS.keys())
    weights = [POWERUP_WEIGHTS[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]
