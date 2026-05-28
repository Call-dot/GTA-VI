# npc = non player car
import pygame

class Npc(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y, speed):
        super().__init__()

        self.game = game
        self.image = image
        self.base_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self, dt):
        apparent_speed = self.speed - self.game.playerspeed
        self.rect.y += apparent_speed * dt

        angle = 180 if self.speed > 0 else 0
        self.image = pygame.transform.rotate(self.base_image, angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.kill()