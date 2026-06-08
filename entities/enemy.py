# npc = non player car
import pygame
from systems.powerups import *
from settings import *

class Police(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y, speed, lane_index, dir):
        super().__init__()

        self.game = game
        self.image = image
        self.base_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.lane_index = lane_index
        self.dir = dir
        self.world_x = x
        self.world_y = y
        self.t = 0
        self.angle = 0
        self.boom = None

    def update(self, dt):
        if self.boom:
            self.yeet(self.boom)
            return

        self.t += dt

        if self.t < 6.7:
            apparent_speed = 21
        else:
            if self.game.speeding:
                apparent_speed = self.speed - ULTRA_SPEED
            else:
                apparent_speed = self.speed - self.game.playerspeed
        
        self.world_y += apparent_speed * dt
        self.rect.center = (self.game.player_x, self.world_y)

        self.angle = self.game.playerangle + 180
        self.image = pygame.transform.rotate(self.base_image, self.angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.game.chased = False
            self.kill()

    def yeet(self, origin):
        dx = origin["origin_x"] - self.world_x
        dy = origin["origin_y"] - self.world_y
        self.hitbox = None
        self.world_x -= BLAST_POWER * dx / dy
        self.world_y -= BLAST_POWER * dy / dx
        self.rect.center = (self.world_x, self.world_y)
        self.angle += 2 * dy / dx
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        if (
            self.world_x < -200 or self.world_x > WIDTH+200 
            or self.world_y < -200 or self.world_y > HEIGHT+200
        ):
            self.kill()
