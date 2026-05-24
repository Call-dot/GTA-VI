import pygame
from settings import *
from systems.asset_loader import AssetLoader
from entities.tile import Tile


NAME = "GTA6"
WIDTH = 1068
HEIGHT = 768
X_CENTRE = WIDTH / 2
Y_CENTRE = HEIGHT / 2

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
        # Braking = 2
        # Neutral = 0
        self.playermode = 0
        # This variable is updated by another function when player presses down arrow
        # Pixels per second downward
        self.playerspeed = 0
        # This variable controls whether the player is going:
        # straight = 0
        # left = 1
        # right = 2
        self.playerdir = 0

        self.brake_power = 2
        self.friction = 0.67 #px/s^2
        self.max_speed = 300
        
        # Utils
        self.tile_size_y = 90
        self.tile_size_x = 110
        self.line_size_y = 90
        self.line_size_x = 10
        self.tiles = []
        self.scroll_offset = 0
        self.x_offset = 0
        self.ts_down = 0
        self.bg_tiler_init()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(30) / 1000
            self.events()
            self.playerinput(self.dt)
            self.update()
            self.bg_tiler()
            self.draw()
            print(len(self.tiles))

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
            self.playermode = 1
            self.accelerate()
            self.debug("FORWARD!")
        elif keys[pygame.K_UP]:
            self.playermode = 2
            self.decelerate(self.brake_power)
        else:
            self.playermode = 0
            self.decelerate(self.friction)

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
        
    def decelerate(self, friction):
        deceleration = (0 - self.playerspeed) * friction
        print(self.playerspeed, "+=", deceleration, "*", self.dt)
        self.playerspeed += deceleration * self.dt

    def left_right(self, dt):
        pass

    def update(self):
        self.all_sprites.update(self.dt)

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.bg_blitter()
        self.all_sprites.draw(self.screen)        
        self.screen.blit(
            self.assets.get_image("weathered_pattern_5"),
            (X_CENTRE + 300, Y_CENTRE - 100 + self.playerspeed)
        )
        pygame.draw.rect(self.screen, "Green", (100, 200, 167, 169))
        pygame.display.flip()

    def bg_generator(self):
        """Generates strings for bgtiler"""
        # R = road
        # L = white line
        # Y = yellow line
        # _ = placeholder
        return "_RLRYRLR_"


    def bg_tiler(self):
        """Generates a text file which represents the road that gets sent to bg_blitter"""
        self.scroll_offset += self.playerspeed * self.dt

        while self.scroll_offset >= self.tile_size_y:
            self.scroll_offset -= self.tile_size_y
            self.tiles.pop()
            self.tiles.insert(
                0,
                self.bg_generator()
            )

    def bg_tiler_init(self):
        rows_needed = HEIGHT // self.tile_size_y + 5
        for _ in range(rows_needed):
            self.tiles.append("__RLRYRLR__")

    def bg_blitter(self):
        """Renders the text from bg_tiler into road images"""
        for row_index, row in enumerate(self.tiles):
            y = (row_index - 1) * self.tile_size_y + self.scroll_offset
            road_width = (len(row) - 1) / 2 * (self.tile_size_x + self.line_size_x)
            x_start = X_CENTRE - road_width / 2
            #half_road_width = (len(row) - 1) / 2 * (self.tile_size_x + self.line_size_x) + self.line_size_x * 2
            
            for col_index, char in enumerate(row):
                if char == "R":
                    img = self.assets.get_image("road_tile")

                elif char == "L":
                    img = self.assets.get_image("white_dashed_road_line")

                elif char == "Y":
                    img = self.assets.get_image("yellow_solid_road_line")
                
                else:
                    continue
                
                img_rect = img.get_rect()
                img_rect.center = (x_start + (self.tile_size_x + self.line_size_x) / 2 * col_index, y)

                self.screen.blit(img, img_rect)
                

        
    def debug(self, msg):
        print("\n", msg)
        print("playermode:", self.playermode)
        print("playerspeed:", self.playerspeed)
        print("playerdir:", self.playerdir)
        print("ts_down:", self.ts_down)


if __name__ == "__main__":
    pygame.init()

    game = Game()
    game.run()

    pygame.quit()