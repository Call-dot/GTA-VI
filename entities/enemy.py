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
        self.t = 0


    def update(self, dt):
        self.t += dt

        if self.t < 6.7:
            apparent_speed = 21
        else:
            apparent_speed = self.speed - self.game.playerspeed
        
        self.world_y += apparent_speed * dt
        self.rect.center = (self.game.player_x, self.world_y)

        angle = self.game.playerangle + 180
        self.image = pygame.transform.rotate(self.base_image, angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.kill()