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
    "suspension": {
        "label": "suspension",
        "color": (255, 80, 80),
        "icon": "suspension",
    }
}

# None = no powerup
POWERUP_WEIGHTS = {
    None:    67,
    "speed": 16,
    "bomb":  12,
    "suspension": 5,
}

BLAST_RADIUS = 350
BLAST_POWER = 42

ULTRA_SPEED = 690
SPEED_POWERUP_DURATION = 8.0

FLUTTER_JUMP_DURATION = 67

def weighted_random_powerup():
    """Return a powerup key (or None) sampled according to POWERUP_WEIGHTS."""
    import random
    keys    = list(POWERUP_WEIGHTS.keys())
    weights = [POWERUP_WEIGHTS[k] for k in keys]
    return random.choices(keys, weights=weights, k=1)[0]
