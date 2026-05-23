import pygame
from settings import *
from systems.asset_loader import AssetLoader
from entities.tile import Tile


NAME = "GTA6"
WIDTH = 1068
HEIGHT = 768
X_CENTRE = WIDTH / 2
Y_CENTRE = HEIGHT / 2
TILESIZE = 1

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()

        self.assets = AssetLoader()
        self.assets.load_images()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(30) / 1000
            self.events()
            self.update()
            self.bg()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.all_sprites.update(self.dt)

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.all_sprites.draw(self.screen)        
        self.screen.blit(
            self.assets.get_image("road_tile"),
            (X_CENTRE, Y_CENTRE)
        )
        print("drawing")
        pygame.display.flip()

    def bg(self):
        self.road_tiles = []

        road_img = self.assets.get_image("road_tile")

        for y in range(-2, HEIGHT // TILESIZE + 2):
            for x in range(WIDTH // TILESIZE):
                tile = Tile(self, road_img, x * TILESIZE, y * TILESIZE)
                self.road_tiles.append(tile)

if __name__ == "__main__":
    pygame.init()

    game = Game()
    game.run()

    pygame.quit()