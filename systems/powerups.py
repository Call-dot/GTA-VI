POWERUP_TYPES = {
    None: {
        "label": None,
        "color": None,
        "icon": None,
    },
    "speed": {
        "label": "speed",
        "color": (255, 220, 50),
        "icon": "gas",
    },
    "bomb": {
        "label": "bomb",
        "color": (255, 80, 80),
        "icon": "bomb",
    },
}

# None = no powerup
POWERUP_WEIGHTS = {
    None:    70,
    "speed": 18,
    "bomb":  12,
}

BOMB_RADIUS = 350

SPEED_POWERUP_DURATION = 8.0

def weighted_random_powerup():
    """Return a powerup key (or None) sampled according to POWERUP_WEIGHTS."""
    import random
    keys    = list(POWERUP_WEIGHTS.keys())
    weights = [POWERUP_WEIGHTS[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]
