from entities.enemy import Enemy
import pygame
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y, image):
        super().__init__()

        self.game = game
        self.image_original = image
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))

        self.x = x
        self.y = y

        self.speed = 250
        self.turn_speed = 4
        self.vx = 0

