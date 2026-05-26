#UNUSED, example syntax for later
import pygame

class Example(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y):
        #Adds the tile to game.all_sprites
        super().__init__(game.all_sprites)

        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 20  # pixels per second downward

    def update(self, dt):
        self.rect.y += self.speed * dt

# #In main.py:
# from entities.tile import Tile
# #self.road_tiles = []

# road_img = self.assets.get_image("road_tile")
# babyblue_car = self.assets.get_image("babyblue_car")

# for y in range(-2, HEIGHT // TILESIZE + 2):
#     for x in range(WIDTH // TILESIZE):
#         tile = Example(self, babyblue_car, x * TILESIZE, y * TILESIZE)
#         self.road_tiles.append(tile)