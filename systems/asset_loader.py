import pygame
import random
from pathlib import Path

class AssetLoader:
    def __init__(self):
        self.fonts = {}
        self.images = {}
        self.music = {}
        self.sound = {}
        self.car_models = ["red_car", "pink_car", "babyblue_car", "camo_car", "darkblue_car", "name_car", "orange_car", "black_car", "lime_car"]
        self.trees = ["tree1", "tree2", "tree3", "tree4", "tree5", "snowpine", "snowtree"]

    def load_fonts(self):
        font_dir = Path("assets/fonts")

        self.fonts["honk"] = pygame.font.Font(
            font_dir / "Honk-Regular-VariableFont_MORF,SHLN.ttf", 64
        )

        self.fonts["ops"] = pygame.font.Font(
            font_dir / "BlackOpsOne-Regular.ttf", 64
        )

        self.fonts["rubik"] = pygame.font.Font(
            font_dir / "RubikMonoOne-Regular.ttf", 32
        )

        self.fonts["bungee"] = pygame.font.Font(
            font_dir / "Bungee-Regular.ttf", 32
        )

        self.fonts["tiny"] = pygame.font.Font(
            font_dir / "Bungee-Regular.ttf", 12
        )

        self.fonts["bungeeshade"] = pygame.font.Font(
            font_dir / "BungeeShade-Regular.ttf", 50
        )

        self.fonts["pixelify"] = pygame.font.Font(
            font_dir / "PixelifySans-Regular.ttf", 50
        )

        self.fonts["pixelify_medium"] = pygame.font.Font(
            font_dir / "PixelifySans-Medium.ttf", 50
        )

        self.fonts["pixelify_bold"] = pygame.font.Font(
            font_dir / "PixelifySans-Bold.ttf", 50
        )

        self.fonts["pixelify_semibold"] = pygame.font.Font(
            font_dir / "PixelifySans-SemiBold.ttf", 50
        )

    def load_images(self):
        image_dir = Path("assets/images")

        self.images["road_tile"] = pygame.image.load(
            image_dir / "road_tile.png"
        ).convert_alpha()

        self.images["sidewalk_tile"] = pygame.image.load(
            image_dir / "sidewalk_tile.png"
        ).convert_alpha()

        self.images["crosswalk"] = pygame.image.load(
            image_dir / "crosswalk.png"
        ).convert_alpha()

        self.images["U_sideroad_sidewalk"] = pygame.image.load(
            image_dir / "U_sideroad_sidewalk.png"
        ).convert_alpha()

        self.images["D_sideroad_sidewalk"] = pygame.image.load(
            image_dir / "D_sideroad_sidewalk.png"
        ).convert_alpha()

        self.images["L_concrete_tile"] = pygame.image.load(
            image_dir / "L_concrete_tile.png"
        ).convert_alpha()

        self.images["R_concrete_tile"] = pygame.image.load(
            image_dir / "R_concrete_tile.png"
        ).convert_alpha()

        self.images["UL_concrete_corner"] = pygame.image.load(
            image_dir / "UL_concrete_corner.png"
        ).convert_alpha()

        self.images["UR_concrete_corner"] = pygame.image.load(
            image_dir / "UR_concrete_corner.png"
        ).convert_alpha()

        self.images["DL_concrete_corner"] = pygame.image.load(
            image_dir / "DL_concrete_corner.png"
        ).convert_alpha()

        self.images["DR_concrete_corner"] = pygame.image.load(
            image_dir / "DR_concrete_corner.png"
        ).convert_alpha()

        self.images["UL_corner"] = pygame.image.load(
            image_dir / "UL_corner.png"
        ).convert_alpha()

        self.images["UR_corner"] = pygame.image.load(
            image_dir / "UR_corner.png"
        ).convert_alpha()

        self.images["DL_corner"] = pygame.image.load(
            image_dir / "DL_corner.png"
        ).convert_alpha()

        self.images["DR_corner"] = pygame.image.load(
            image_dir / "DR_corner.png"
        ).convert_alpha()

        self.images["UL_concrete_merge"] = pygame.image.load(
            image_dir / "UL_concrete_merge.png"
        ).convert_alpha()

        self.images["UR_concrete_merge"] = pygame.image.load(
            image_dir / "UR_concrete_merge.png"
        ).convert_alpha()

        self.images["DL_concrete_merge"] = pygame.image.load(
            image_dir / "DL_concrete_merge.png"
        ).convert_alpha()

        self.images["DR_concrete_merge"] = pygame.image.load(
            image_dir / "DR_concrete_merge.png"
        ).convert_alpha()

        self.images["weathered_pattern_1"] = pygame.image.load(
            image_dir / "weathered_pattern_1.png"
        ).convert_alpha()

        self.images["weathered_pattern_2"] = pygame.image.load(
            image_dir / "weathered_pattern_2.png"
        ).convert_alpha()

        self.images["weathered_pattern_3"] = pygame.image.load(
            image_dir / "weathered_pattern_3.png"
        ).convert_alpha()

        self.images["weathered_pattern_4"] = pygame.image.load(
            image_dir / "weathered_pattern_4.png"
        ).convert_alpha()

        self.images["weathered_pattern_5"] = pygame.image.load(
            image_dir / "weathered_pattern_5.png"
        ).convert_alpha()

        self.images["weathered_pattern_6"] = pygame.image.load(
            image_dir / "weathered_pattern_6.png"
        ).convert_alpha()

        self.images["weathered_pattern_7"] = pygame.image.load(
            image_dir / "weathered_pattern_7.png"
        ).convert_alpha()

        self.images["weathered_pattern_8"] = pygame.image.load(
            image_dir / "weathered_pattern_8.png"
        ).convert_alpha()

        self.images["curb"] = pygame.image.load(
            image_dir / "curb.png"
        ).convert_alpha()

        self.images["no_road_line"] = pygame.image.load(
            image_dir / "no_road_line.png"
        ).convert_alpha()

        self.images["white_dashed_road_line"] = pygame.image.load(
            image_dir / "white_dashed_road_line.png"
        ).convert_alpha()

        self.images["white_solid_road_line"] = pygame.image.load(
            image_dir / "white_dashed_road_line.png"
        ).convert_alpha()

        self.images["yellow_solid_road_line"] = pygame.image.load(
            image_dir / "yellow_solid_road_line.png"
        ).convert_alpha()

        self.images["yellow_dashed_road_line"] = pygame.image.load(
            image_dir / "yellow_dashed_road_line.png"
        ).convert_alpha()

        self.images["R_light"] = pygame.image.load(
            image_dir / "R_light.png"
        ).convert_alpha()

        self.images["RY_light"] = pygame.image.load(
            image_dir / "RY_light.png"
        ).convert_alpha()

        self.images["Y_light"] = pygame.image.load(
            image_dir / "Y_light.png"
        ).convert_alpha()

        self.images["G_light"] = pygame.image.load(
            image_dir / "G_light.png"
        ).convert_alpha()

        self.images["school_sign"] = pygame.image.load(
            image_dir / "school_sign.png"
        ).convert_alpha()
        
        self.images["tutorial"] = pygame.image.load(
            image_dir / "tutorial.png"
        ).convert_alpha()

        def load_car(model):
            self.images[model] = pygame.image.load(
                image_dir / f"{model}.png"
            ).convert_alpha()

        for car in self.car_models:
            load_car(car)
        
        self.images["star"] = pygame.image.load(
            image_dir / "star.png"
        ).convert_alpha()

        self.images["snow"] = pygame.image.load(
            image_dir / "snow.png"
        ).convert_alpha()

        self.images["grass"] = pygame.image.load(
            image_dir / "grass.png"
        ).convert_alpha()

        self.images["sand"] = pygame.image.load(
            image_dir / "sand.png"
        ).convert_alpha()

        self.images["sandy"] = pygame.image.load(
            image_dir / "sandy.png"
        ).convert_alpha()

        self.images["savan"] = pygame.image.load(
            image_dir / "savan.png"
        ).convert_alpha()

        self.images["deadtree"] = pygame.image.load(
            image_dir / "deadtree.png"
        ).convert_alpha()

        self.images["deadbush"] = pygame.image.load(
            image_dir / "deadbush.png"
        ).convert_alpha()

        def load_tree(tree):
            self.images[tree] = pygame.image.load(
                image_dir / f"{tree}.png"
            ).convert_alpha()

        for tree in self.trees:
            load_tree(tree)

        self.images["policecar"] = pygame.image.load(
            image_dir / "policecar.png"
        ).convert_alpha()

        self.images["policecar1"] = pygame.image.load(
            image_dir / "policecar1.png"
        ).convert_alpha()  

        self.images["speedup"] = pygame.image.load(
            image_dir / "speedup.png"
        ).convert_alpha()

        self.images["speedup1"] = pygame.image.load(
            image_dir / "speedup1.png"
        ).convert_alpha()

        self.images["logo"] = pygame.image.load(
            image_dir / "logo.png"
        ).convert_alpha()

        self.images["ghost"] = pygame.image.load(
            image_dir / "ghost.png"
        ).convert_alpha()

        self.images["gas"] = pygame.image.load(
            image_dir / "gas.png"
        ).convert_alpha()

        self.images["bomb"] = pygame.image.load(
            image_dir / "bomb.png"
        ).convert_alpha()

        self.images["strockstar"] = pygame.image.load(
            image_dir / "strockstar.png"
        ).convert_alpha()

    def load_music(self):
        music_dir = Path("assets/music")

        self.music["theme"] = music_dir / "GTA6_theme_song.mp3"
        self.music["title"] = music_dir / "titlemusic.mp3"
        self.music["menu"] = music_dir / "menumusic.wav"
        self.music["police"] = music_dir / "guardian_theme.mp3"
        self.music["shepard"] = music_dir / "shepard.mp3"
        self.music["speed"] = music_dir / "freebird.mp3"

    def load_sounds(self):
        sound_dir = Path("assets/sounds")

        self.sound["slap"] = pygame.mixer.Sound(
            sound_dir / "slap.mp3"
        )
        self.sound["slap"].set_volume(0.4)

        self.sound["kid_slap"] = pygame.mixer.Sound(
            sound_dir / "kid-slap-oh.mp3"
        )
        self.sound["kid_slap"].set_volume(0.5)

        self.sound["slip"] = pygame.mixer.Sound(
            sound_dir / "slip.mp3"
        )
        self.sound["slip"].set_volume(0.9)

        self.sound["boom"] = pygame.mixer.Sound(
            sound_dir / "vine-boom.mp3"
        )
        self.sound["boom"].set_volume(0.8)

    def get_font(self, name):
        return self.fonts[name]

    def get_image(self, name):
        return self.images[name]

    def get_music(self, name):
        return self.music[name]
    
    def get_sound(self, name):
        return self.sound[name]

    def get_random_car(self, player=None):
        name = ""
        while name == player or name == "":
            name = random.choice(self.car_models)
        return name, self.images[name]