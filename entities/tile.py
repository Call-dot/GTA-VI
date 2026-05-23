# entities/tile.py
import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y):
        super().__init__(game.all_sprites)

        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 200  # pixels per second downward

    def update(self, dt):
        self.rect.y += self.speed * dt