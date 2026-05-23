import pygame
from settings import *
from systems.asset_loader import AssetLoader
from entities.tile import Tile


NAME = "GTA6"
WIDTH = 1068
HEIGHT = 768
X_CENTRE = WIDTH / 2
Y_CENTRE = HEIGHT / 2
TILESIZE = 2

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()

        # Run AssetLoader and save it in self.assets
        self.assets = AssetLoader()
        self.assets.load_images()

        # This variable controls whether the player is currently trying to accelerate
        # Is directly updated by player
        # Accelerating = 1
        # Braking = 0
        self.playermode = 0
        # This variable is updated by another function when player presses down arrow
        # Pixels per second downward
        self.playerspeed = 0
        # This variable controls whether the player is going:
        # straight = 0
        # left = 1
        # right = 2
        self.playerdir = 0

        self.friction = -10 #px/s^2
        self.max_speed = 300
        
        # Timestamps
        self.ts_down = 0

    def run(self):
        while self.running:
            self.dt = self.clock.tick(30) / 1000
            self.events()
            self.playerinput(self.dt)
            self.update()
            self.bg_blitter()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    self.ts_down = self.dt

    def playerinput(self, dt):
        keys = pygame.key.get_pressed()
        
        # Fast/slow
        if keys[pygame.K_DOWN]:
            self.accelerate()
            self.debug("FORWARD!")
        else:
            self.decelerate()
            # self.debug("SLOW DOWN!")

        # Steering
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.playerdir = 1
            self.debug("LEFT!")
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.playerdir = 2
            self.debug("RIGHT!")
        else:
            self.playerdir = 0

    def accelerate(self):
        acceleration = (self.max_speed - self.playerspeed) * 2
        self.playerspeed += acceleration * self.dt
        
    def decelerate(self):
        deceleration = (0 - self.playerspeed) * 2
        print(self.playerspeed, "+=", deceleration, "*", self.dt)
        self.playerspeed += deceleration * self.dt

    def left_right(self, dt):
        pass

    def update(self):
        self.all_sprites.update(self.dt)

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.all_sprites.draw(self.screen)        
        self.screen.blit(
            self.assets.get_image("road_tile"),
            (X_CENTRE + self.playerspeed, Y_CENTRE)
        )
        pygame.display.flip()

    def bg_tiler(self):
        """Generates a text file which represents the road that gets sent to bg_blitter"""

    def bg_blitter(self):
        """Renders the text from bg_tiler into road images"""
        
    def debug(self, msg):
        print(msg)
        print("playermode:", self.playermode)
        print("playerspeed:", self.playerspeed)
        print("playerdir:", self.playerdir)
        print("ts_down:", self.ts_down)


if __name__ == "__main__":
    pygame.init()

    game = Game()
    game.run()

    pygame.quit()