import pygame
import random
from settings import *
from systems.asset_loader import AssetLoader
from entities.tiler import Tiler
from levels.biomes import BIOMES

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
REVERSE_SPEED = -67
HANDLING = 5              # larger = snappier
AUTO_LANE_ALIGN = True
DEBUG = True

TILE_SIZE_Y = 90
TILE_SIZE_X = 110
LINE_SIZE_Y = 90
LINE_SIZE_X = 10
NUM_WEATHERING_PATTERNS = 8
DRIVING_SIDE = "right"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        random.seed(SEED)
        print(SEED)

        self.car_options = ["red_car", "pink_car", "camo_car", "babyblue_car",]
        self.player_img = None

        # Run AssetLoader and save it in self.assets
        self.assets = AssetLoader()
        self.assets.load_images()
        self.assets.load_music()

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
        self.t = 0
        self.tiles = []
        self.weathering = []
        self.trees = []
        self.rocks = []
        self.scroll_offset = 0
        self.x_offset = 0
        self.ts_down = 0
        self.bg_tiler_init()
        self.current_biome = BIOMES["forest"]

        if DEBUG:
            self.corner_test = True

    def run(self):
        self.select_car_menu()
        while self.running:
            self.dt = self.clock.tick(30) / 1000
            self.t += self.dt
            self.events()
            self.playerinput(self.dt)
            self.player()
            self.update()
            self.bg_tiler()
            self.draw()
            if DEBUG:
                print(len(self.tiles))

    def select_car_menu(self):
        """Displays a car selection menu before starting the game."""
        selecting = True
        font = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Define layout parameters for the selection cards
        card_w, card_h = 200, 200
        spacing = 40
        start_x = X_CENTRE - ((card_w * 4 + spacing * 3) / 2)
        y_pos = Y_CENTRE - 50

        # Construct collision bounding rects for each choice
        rects = []
        for i in range(4):
            x = start_x + i * (card_w + spacing)
            rects.append(pygame.Rect(x, y_pos, card_w, card_h))

        while selecting:
            self.screen.fill((40, 40, 45))
            
            # Title text rendering
            title_surf = font.render("CHOOSE YOUR VEHICLE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 4))
            self.screen.blit(title_surf, title_rect)

            # Event loop monitoring selection input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Evaluate if choice regions intersect click coordinates
                    for idx, rect in enumerate(rects):
                        if rect.collidepoint(mouse_pos):
                            chosen_key = self.car_options[idx]
                            self.player_img = self.assets.get_image(chosen_key)
                            selecting = False # Exit selection loop, initializing run sequence
            
            # Rendering cards and visual feedback
            mouse_pos = pygame.mouse.get_pos()
            for idx, rect in enumerate(rects):
                # Hover detection styling
                if rect.collidepoint(mouse_pos):
                    color = (0, 200, 100)
                    border = 6
                else:
                    color = (200, 200, 200)
                    border = 2
                
                pygame.draw.rect(self.screen, color, rect, border, border_radius=10)
                
                # Fetch corresponding asset and render centralized inside card UI
                car_surface = self.assets.get_image(self.car_options[idx])
                car_rect = car_surface.get_rect(center=rect.center)
                self.screen.blit(car_surface, car_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    self.ts_down = self.dt
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos 
                print(f"Mouse Clicked at X: {mouse_x}, Y: {mouse_y}")

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
            self.reverse(BRAKE_POWER)
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

    def reverse(self, friction):
        deceleration = (REVERSE_SPEED - self.playerspeed) * friction
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
        self.player_vx *= (self.playerspeed / MAX_SPEED)

        # Move car
        self.player_x += self.player_vx * self.dt
        #Boundaries
        if self.player_x > WIDTH+50:
            self.player_x = -40
        
        elif self.player_x < -50:
            self.player_x = WIDTH+40

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

        half_width = rect.width / 2
        
        #if self.player_x < half_width:
            #ghost_rect = player_rotated.get_rect(center=(self.player_x + WIDTH, self.player_y))
            #self.screen.blit(player_rotated, ghost_rect)
            
        #elif self.player_x > WIDTH - half_width:
            #ghost_rect = player_rotated.get_rect(center=(self.player_x - WIDTH, self.player_y))
            #self.screen.blit(player_rotated, ghost_rect)

        pygame.draw.rect(self.screen, "Green", (X_CENTRE + 300, Y_CENTRE - 300 + self.playerspeed, 167, 169))
        pygame.display.flip()

    def scenery_generator(self, type=None):
        """Carey this is for you, I want this function to generate random scenery"""
        if type == "tree":
            pass #tree generator
        elif type == "rocks":
            pass #rock generator
        #If you don't know how to go about this, do as I've done for bg_generator() 
    
    def scenery_tiler(self):
        """
        Carey this is also for you, this function should do the same thing as bg_tiler() but for trees + rocks
        Save your trees and rocks in self.trees and self.rocks
        """
        pass
    
    def scenery_blitter(self):
        """
        Carey this is also for you, this function should do the same thing as bg_blitter() but for trees + rocks
        Scenery should only render in locations not covered by a road
        """
        pass

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
            if self.t < 10:
                return "__S|.|.|S__"
            elif self.t < 20:
                return "SC./.|./.CS"
            elif self.corner_test:
                self.corner_test = False
                return "1-./.|./.-2"
            else:
                return "_-./.|./.C_"

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
            self.tiles.append("__.|.|.|.__")
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
                if char == ".":
                    img = self.assets.get_image("road_tile")
                    weathering = self.assets.get_image("weathered_pattern_" + self.weathering[row_index][col_index // 2])

                elif char == "S":
                    img = self.assets.get_image("sidewalk_tile")
                
                elif char == "C":
                    img = self.assets.get_image("curb")
                
                elif char == "-":
                    img = self.assets.get_image("no_road_line")

                elif char == "/":
                    img = self.assets.get_image("white_dashed_road_line")

                elif char == "|":
                    img = self.assets.get_image("yellow_solid_road_line")
                
                elif char == "<":
                    img = self.assets.get_image("L_concrete_tile")

                elif char == ">":
                    img = self.assets.get_image("R_concrete_tile")

                elif char == "1":
                    img = self.assets.get_image("UL_concrete_corner")

                elif char == "2":
                    img = self.assets.get_image("UR_concrete_corner")

                elif char == "3":
                    img = self.assets.get_image("DL_concrete_corner")
                
                elif char == "4":
                    img = self.assets.get_image("DR_concrete_corner")


                else:
                    continue
                
                img_rect = img.get_rect()
                img_rect.center = (x_start + (TILE_SIZE_X + LINE_SIZE_X) / 2 * col_index, y)

                self.screen.blit(img, img_rect)
                if char == ".":
                    self.screen.blit(weathering, img_rect)
                if char == "S":
                    pass
                

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