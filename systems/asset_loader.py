import pygame
from pathlib import Path

class AssetLoader:
    def __init__(self):
        self.images = {}

    def load_images(self):
        image_dir = Path("assets/images")

        self.images["road_tile"] = pygame.image.load(
            image_dir / "road_tile.png"
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

        self.images["camo_car"] = pygame.image.load(
            image_dir / "camo_car.png"
        ).convert_alpha()

    def get_image(self, name):
        return self.images[name]