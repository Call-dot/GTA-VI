# npc = non player car
import pygame

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


    def update(self, dt):
        apparent_speed = self.speed - self.game.playerspeed
        
        self.world_y += apparent_speed * dt
        self.rect.center = (self.world_x, self.world_y)

        angle = 180 if self.speed > 0 else 0
        self.image = pygame.transform.rotate(self.base_image, angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.kill()