import pygame
from pathlib import Path

class AssetLoader:
    def __init__(self):
        self.images = {}
        self.music = {}

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

        self.images["red_car"] = pygame.image.load(
            image_dir / "red_car.png"
        ).convert_alpha()

        self.images["pink_car"] = pygame.image.load(
            image_dir / "pink_car.png"
        ).convert_alpha()

        self.images["babyblue_car"] = pygame.image.load(
            image_dir / "babyblue_car.png"
        ).convert_alpha()

        self.images["black_car"] = pygame.image.load(
            image_dir / "black_car.png"
        ).convert_alpha()

        self.images["lime_car"] = pygame.image.load(
            image_dir / "lime_car.png"
        ).convert_alpha()

        self.images["camo_car"] = pygame.image.load(
            image_dir / "camo_car.png"
        ).convert_alpha()

    def load_music(self):
        music_dir = Path("assets/music")

        self.music["theme"] = music_dir / "GTA6_theme_song.mp3"

    def get_image(self, name):
        return self.images[name]

    def get_music(self, name):
        return self.music[name]