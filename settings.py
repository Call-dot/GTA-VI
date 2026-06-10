import random

NAME = "GTA6"
WIDTH = 1068
HEIGHT = 768
X_CENTRE = WIDTH / 2
Y_CENTRE = HEIGHT / 2

SPACE_ABOVE_PLAYER = 420
BRAKE_POWER = 2
FRICTION = 0.67 #px/s^2
AIR_RESISTANCE = 0.08
MAX_SPEED = 420
MAX_TURN_SPEED = 420      # px/s
REVERSE_SPEED = -69
HANDLING = 5              # larger = snappier
AIRTIME = 2
AUTO_LANE_ALIGN = True
DEBUG = False
HITBOX = True
HITBOX_TOLERANCE = 21
SPAWNCAMP_DELAY = 2000
CATCH_DISTANCE = 217
END_THRESHOLD = 30

TILE_SIZE_Y = 90
TILE_SIZE_X = 110
LINE_SIZE_Y = 90
LINE_SIZE_X = 10
SCENE_SIZE_X = 50
SCENE_SIZE_Y = 500
ROAD_SIZE_X = (TILE_SIZE_X + LINE_SIZE_X) / 2
NUM_WEATHERING_PATTERNS = 8
NOT_BRITISH_DRIVING = False
TRAFFIC = 0.02

MIN_LIGHT_TIME = 5
MAX_LIGHT_TIME = 60
QUEUE_INTENSITY = 0.067
TIMEWARP = 2
QUEUE_TIMEWARP = 10
SCHOOL_DISTANCE = 420
DEPARTURE_TIME = 30000
DEADLINE = 30600

CAR_MODELS = [
            {"speed": 85, "control": 70, "lives": 3, "auto_align": 90},
            {"speed": 95, "control": 60, "lives": 2, "auto_align": 40},
            {"speed": 60, "control": 90, "lives": 4, "auto_align": 85},
            {"speed": 75, "control": 75, "lives": 3, "auto_align": 70},
            {"speed": 90, "control": 65, "lives": 2, "auto_align": 50},
            {"speed": 50, "control": 95, "lives": 5, "auto_align": 95},
            {"speed": 80, "control": 80, "lives": 3, "auto_align": 60},
            {"speed": 100, "control": 50, "lives": 1, "auto_align": 30},
            {"speed": 70, "control": 85, "lives": 4, "auto_align": 80}
        ]