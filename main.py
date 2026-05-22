import pygame
from settings import *

NAME = "GTA6"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1000, 1000))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True

        self.all_sprites = pygame.sprite.Group()

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()

    game = Game()
    game.run()

    pygame.quit()