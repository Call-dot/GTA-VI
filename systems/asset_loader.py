import pygame
import random
from pathlib import Path

class AssetLoader:
    def __init__(self):
        self.images = {}
        self.music = {}
        self.car_models = ["red_car", "pink_car", "babyblue_car", "camo_car", "darkblue_car", "name_car", "orange_car", "black_car", "lime_car"]

    def load_images(self):
        image_dir = Path("assets/images")

        self.images["road_tile"] = pygame.image.load(
            image_dir / "road_tile.png"
        ).convert_alpha()

        self.images["sidewalk_tile"] = pygame.image.load(
            image_dir / "sidewalk_tile.png"
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

        self.images["yellow_solid_road_line"] = pygame.image.load(
            image_dir / "yellow_solid_road_line.png"
        ).convert_alpha()

        self.images["yellow_dashed_road_line"] = pygame.image.load(
            image_dir / "yellow_dashed_road_line.png"
        ).convert_alpha()

        def load_car(model):
            self.images[model] = pygame.image.load(
                image_dir / f"{model}.png"
            ).convert_alpha()

        for car in self.car_models:
            load_car(car)

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

        self.images["deadtree"] = pygame.image.load(
            image_dir / "deadtree.png"
        ).convert_alpha()
        
        self.images["star"] = pygame.image.load(
            image_dir / "star.png"
        ).convert_alpha()

        self.images["deadbush"] = pygame.image.load(
            image_dir / "deadbush.png"
        ).convert_alpha()

        self.images["snowtree"] = pygame.image.load(
            image_dir / "snowtree.png"
        ).convert_alpha()
        
    def load_music(self):
        music_dir = Path("assets/music")

        self.music["theme"] = music_dir / "GTA6_theme_song.mp3"
        self.music["menu"] = music_dir / "menumusic.wav"

    def get_image(self, name):
        return self.images[name]

    def get_music(self, name):
        return self.music[name]

    def get_random_car(self, player=None):
        name = ""
        while name == player or name == "":
            name = random.choice(self.car_models)
        return name, self.images[name]