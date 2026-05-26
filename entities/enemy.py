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

    def update(self, dt):
        self.chase_player(dt)

        #move vertically
        self.y += (self.speed - self.game.playerspeed) * dt

        #move horizontally
        self.x += self.vx * dt

        #update
        self.rect.center = (self.x, self.y)

        #rotate turning
        angle = -self.vx * 0.05

        self.image = pygame.transform.rotate(
            self.image_original,
            angle + 180
        )

        self.rect = self.image.get_rect(
            center=self.rect.center
        )

        #Delete enemy off screen
        if self.y > HEIGHT + 200:
            self.kill()

    def chase_player(self, dt):
        player_x = self.game.player_x

        #D to player
        direction = player_x - self.x

        self.vx += direction * self.turn_speed * dt

        #speed limit
        self.vx = max(-250, min(250, self.vx))