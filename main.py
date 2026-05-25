import pygame
import random
from settings import *
from systems.asset_loader import AssetLoader
from entities.tiler import Tiler


NAME = "GTA6"
WIDTH = 1068
HEIGHT = 768
X_CENTRE = WIDTH / 2
Y_CENTRE = HEIGHT / 2
SEED = random.randrange(2147483647)

BRAKE_POWER = 2
FRICTION = 0.67 #px/s^2
MAX_SPEED = 420
MAX_TURN_SPEED = 300      # px/s
HANDLING = 5              # larger = snappier
AUTO_LANE_ALIGN = True
DEBUG = True

TILE_SIZE_Y = 90
TILE_SIZE_X = 110
LINE_SIZE_Y = 90
LINE_SIZE_X = 10
NUM_WEATHERING_PATTERNS = 8

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        random.seed(SEED)
        print(SEED)

        # Run AssetLoader and save it in self.assets
        self.assets = AssetLoader()
        self.assets.load_images()
        self.assets.load_music()

        self.player_img = self.assets.get_image("red_car")
        pygame.mixer.music.load(
            self.assets.get_music("theme")
        )
        pygame.mixer.music.play(-1)

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

        self.player_x = X_CENTRE
        self.player_y = HEIGHT - 200
        self.player_vx = 0
        
        # Utils
        self.tiles = []
        self.weathering = []
        self.scroll_offset = 0
        self.x_offset = 0
        self.ts_down = 0
        self.bg_tiler_init()

    def run(self):
        while self.running:
            self.dt = self.clock.tick(30) / 1000
            self.events()
            self.playerinput(self.dt)
            self.player()
            self.update()
            self.bg_tiler()
            self.draw()
            if DEBUG:
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
            if DEBUG:
                self.debugger("FORWARD!")
        elif keys[pygame.K_UP]:
            self.playermode = 2
            self.decelerate(BRAKE_POWER)
        else:
            self.playermode = 0
            self.decelerate(FRICTION)

        # Steering
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.playerdir = 1
            if DEBUG:
                self.debugger("LEFT!")
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.playerdir = 2
            if DEBUG:
                self.debugger("RIGHT!")
        else:
            self.playerdir = 0

    def accelerate(self):
        acceleration = (MAX_SPEED - self.playerspeed) * 2
        self.playerspeed += acceleration * self.dt
        
    def decelerate(self, friction):
        deceleration = (0 - self.playerspeed) * friction
        if DEBUG:
            print(self.playerspeed, "+=", deceleration, "*", self.dt)
        self.playerspeed += deceleration * self.dt
    
    def player(self):
        # Desired sideways velocity
        if self.playerdir == 1:
            target_v = -MAX_TURN_SPEED

        elif self.playerdir == 2:
            target_v = MAX_TURN_SPEED

        else:
            if AUTO_LANE_ALIGN:
                target_v = 0
            else:
                target_v = self.player_vx

        # Smoothly approach target velocity
        self.player_vx += (
            target_v - self.player_vx
        ) * HANDLING * self.dt

        # Move car
        self.player_x += self.player_vx * self.dt

    def vibes(self, dt):
        pass

    def update(self):
        self.all_sprites.update(self.dt)

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.bg_blitter()
        self.all_sprites.draw(self.screen)  

        angle = self.player_vx * 0.05
        player_rotated = pygame.transform.rotate(
            self.player_img,
            angle + 180
        )
        rect = player_rotated.get_rect(
            center=(self.player_x, self.player_y)
        )
        self.screen.blit(player_rotated, rect)    
        pygame.draw.rect(self.screen, "Green", (X_CENTRE + 300, Y_CENTRE - 300 + self.playerspeed, 167, 169))
        pygame.display.flip()

    def bg_generator(self, type=None):
        """Generates strings for bgtiler"""
        if type == "weathering":
            pattern_key = ""
            for i in range(8):
                pattern_key = pattern_key + (str(random.randrange(1, NUM_WEATHERING_PATTERNS)))
            return pattern_key
        
        else:
            # R = road
            # L = white line
            # Y = yellow line
            # _ = placeholder
            return "_RLRYRLR_"

    def bg_tiler(self):
        """Generates a text file which represents the road that gets sent to bg_blitter"""
        self.scroll_offset += self.playerspeed * self.dt

        while self.scroll_offset >= TILE_SIZE_Y:
            self.scroll_offset -= TILE_SIZE_Y
            self.tiles.pop()
            self.tiles.insert(0, self.bg_generator())
            self.weathering.pop()
            self.weathering.insert(0, self.bg_generator("weathering"))

    def bg_tiler_init(self):
        rows_needed = HEIGHT // TILE_SIZE_Y + 5
        for _ in range(rows_needed):
            self.tiles.append("__RYRYRYR__")
            self.weathering.append(self.bg_generator("weathering"))
        if DEBUG:
            print(self.weathering)

    def bg_blitter(self):
        """Renders the text from bg_tiler into road images"""
        for row_index, row in enumerate(self.tiles):
            y = HEIGHT - ((row_index - 1) * TILE_SIZE_Y + self.scroll_offset)
            road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X)
            x_start = X_CENTRE - road_width / 2
            #half_road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X) + LINE_SIZE_X * 2
            
            for col_index, char in enumerate(row):
                if char == "R":
                    img = self.assets.get_image("road_tile")
                    weathering = self.assets.get_image("weathered_pattern_" + self.weathering[row_index][col_index // 2])

                elif char == "L":
                    img = self.assets.get_image("white_dashed_road_line")

                elif char == "Y":
                    img = self.assets.get_image("yellow_solid_road_line")
                
                else:
                    continue
                
                img_rect = img.get_rect()
                img_rect.center = (x_start + (TILE_SIZE_X + LINE_SIZE_X) / 2 * col_index, y)

                self.screen.blit(img, img_rect)
                if char == "R":
                    self.screen.blit(weathering, img_rect)
                

    def debugger(self, msg):
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