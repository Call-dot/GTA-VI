import pygame
import random
from settings import *
from systems.asset_loader import AssetLoader
from levels.traffic import Tiler
from levels.biomes import BIOMES
from levels.roads import ROAD_TYPES
from entities.npc import Npc
from entities.enemy import Police
from systems.ui import Ui

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.t = 0
        self.running = True
        self.gaming = False
        self.width = WIDTH
        self.height = HEIGHT
        self.space_above_player = SPACE_ABOVE_PLAYER
        self.all_sprites = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        random.seed(SEED)
        self.tiler = Tiler(
            self,
            seed=SEED,
            driving_side="right" if NOT_BRITISH_DRIVING else "left"
        )
        print(SEED)
        self.not_british_driving = NOT_BRITISH_DRIVING
        self.igt = 0

        # Run AssetLoader and save it in self.assets
        self.assets = AssetLoader()
        self.assets.load_images()
        self.assets.load_music()
        self.assets.load_fonts()
        self.assets.load_sounds()
        self.ui = Ui(self)
        self.fonts = {
            "title": self.assets.get_font("honk"),
            "subtitle": self.assets.get_font("pixelify"),
            "header": self.assets.get_font("ops"),
            "body": self.assets.get_font("bungee"),
            "highlight": self.assets.get_font("rubik"),
            "caption": self.assets.get_font("tiny")
        }

        self.car_options = self.assets.car_models

        self.car_stats_database = {}
        self.stat_presets = CAR_MODELS
        
        for idx, car_key in enumerate(self.car_options):
            preset = self.stat_presets[idx % len(self.stat_presets)]
            self.car_stats_database[car_key] = preset

        self.player_model = None
        self.player_img = None
        self.star_img = self.assets.get_image("star")

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
        # How many rows of tiles the player has passed through
        self.playerpos = 0

        self.player_x = X_CENTRE
        self.player_y = HEIGHT - SPACE_ABOVE_PLAYER
        self.player_vx = 0
        self.player_rect = None
        self.player_hitbox = None
        self.playerangle = 0
        
        # Utils
        self.tiles = []
        self.tile_data = []
        self.weathering = []
        self.trees = []
        self.rocks = []
        self.scroll_offset = 0
        self.x_offset = 0
        self.ts_down = 0
        self.bg_tiler_init()
        self.current_biome = BIOMES["badlands"]

        self.health = 5
        self.flash_timer = 0
        self.flash_interval = 150  # milliseconds
        self.player_opacity = 255
        self.invincible = False
        self.invincible_time = 0
        self.spawncamp_delay = SPAWNCAMP_DELAY  # milliseconds
        self.signal = True
        self.signaltimer = 0
        self.music = [None, False]
        self.sound = [None, None]
        self.chased = False
        self.tutorial = True

        if DEBUG or not(DEBUG):
            self.corner_test = True

    def new_run(self):
        self.health = 5
        self.playerspeed = 0
        self.playerpos = 0
        self.chased = False

        self.player_x = X_CENTRE
        self.player_y = HEIGHT - SPACE_ABOVE_PLAYER
        self.player_vx = 0
        self.player_rect = None
        self.player_hitbox = None
        self.playerangle = 0
        self.tutorial = True

        self.npcs.empty()
        self.enemies.empty()
        self.all_sprites.empty()

        self.tiles.clear()
        self.tile_data.clear()
        self.weathering.clear()
        self.tiler.intersection.clear()

        self.bg_tiler_init()

    def run(self):
        while self.running:
            self.music[1] = False
            self.vlc("menu", -1, False)
            self.ui.select_car_menu()
            self.new_run()
            self.ui.intro_screen()
            while self.gaming:
                self.vlc("theme", -1, False)
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
        print(self.tiles)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gaming = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if self.t > 2:
                    self.tutorial = False
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    self.gaming = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos 
                print(f"Mouse Clicked at X: {mouse_x}, Y: {mouse_y}")

    def playerinput(self, dt):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_DOWN]:
            self.playermode = 1
            self.accelerate()
        elif keys[pygame.K_UP]:
            self.playermode = 2
            self.reverse(BRAKE_POWER)
        else:
            self.playermode = 0
            self.decelerate(FRICTION)
    
        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.playerdir = 1
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.playerdir = 2
        else:
            self.playerdir = 0

    def accelerate(self):
        acceleration = (MAX_SPEED - self.playerspeed) * 2
        self.playerspeed += acceleration * self.dt
        
    def decelerate(self, friction):
        deceleration = (0 - self.playerspeed) * friction
        self.playerspeed += deceleration * self.dt

    def reverse(self, friction):
        deceleration = (REVERSE_SPEED - self.playerspeed) * friction
        self.playerspeed += deceleration * self.dt
    
    def player(self):
        if self.playerdir == 1:
            target_v = -MAX_TURN_SPEED

        elif self.playerdir == 2:
            target_v = MAX_TURN_SPEED

        else:
            if AUTO_LANE_ALIGN:
                target_v = 0
            else:
                target_v = self.player_vx
       
        self.player_vx += (target_v - self.player_vx) * HANDLING * self.dt 
        self.player_vx *= (self.playerspeed / MAX_SPEED)
        self.player_x += self.player_vx * self.dt
        
        if self.player_x > WIDTH+50:
            self.player_x = -40
        elif self.player_x < -50:
            self.player_x = WIDTH+40

    def vibes(self, dt):
        pass

    def update(self):
        current_road = self.tile_data[self.playerpos]
        traffic_density = current_road["road_type"]["traffic"]
        self.igt += self.dt
        if random.random() < traffic_density * self.dt * (self.playerspeed / MAX_SPEED + 0.5):
            self.spawn_npc()
        self.all_sprites.update(self.dt)
        self.collisions()

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.bg_blitter()
        self.all_sprites.draw(self.screen)  

        self.player_img.set_alpha(self.player_opacity)
        self.playerangle = self.player_vx * 0.05
        player_rotated = pygame.transform.rotate(self.player_img, self.playerangle + 180)
        rect = player_rotated.get_rect(
            center=(self.player_x, self.player_y)
        )
        hitbox = rect.inflate(-HITBOX_TOLERANCE, -HITBOX_TOLERANCE)
        self.player_rect = rect
        self.player_hitbox = hitbox
        self.screen.blit(player_rotated, rect)    

        for i in range(self.health):
            self.screen.blit(self.star_img, (20 + i * 40, 20))

        clock_surf = self.fonts["highlight"].render(self.gametime(), True, ("#FEFEFE"))
        clock_rect = clock_surf.get_rect(topleft=(20, 50))
        self.screen.blit(clock_surf, clock_rect)
        half_width = rect.width / 2
        
        #if self.player_x < half_width:
            #ghost_rect = player_rotated.get_rect(center=(self.player_x + WIDTH, self.player_y))
            #self.screen.blit(player_rotated, ghost_rect)
            
        #elif self.player_x > WIDTH - half_width:
            #ghost_rect = player_rotated.get_rect(center=(self.player_x - WIDTH, self.player_y))
            #self.screen.blit(player_rotated, ghost_rect)

        pygame.draw.rect(self.screen, "Green", (X_CENTRE + 300, Y_CENTRE - 300 + self.playerspeed, 167, 169)) # placeholder speedometer
        if HITBOX:
            lane = self.closest_lane()
            font = pygame.font.SysFont(None, 36)
            text = font.render(
                f"Lane: {lane}",
                True,
                (255, 255, 255)
            )

            self.screen.blit(text, (20, 20))
            for npc in self.npcs:
                pygame.draw.line(
                    self.screen,
                    "red",
                    npc.rect.center,
                    (npc.rect.centerx, npc.rect.centery),
                    1
                )
        if self.tutorial:
            self.show_actions()
        pygame.display.flip()

    def spawn_npc(self): #npc = non player car
        _, image = self.assets.get_random_car(self.player_model)
        driving_direction = random.choice(["down", "up"])
        if driving_direction == "down":
            npc_speed = 100 #random.randint(80, 300) #to be modified later
        elif driving_direction == "up":
            npc_speed = -100
        
        player_speed = self.playerspeed
        apparent_speed = npc_speed - player_speed

        if apparent_speed < 0:
            spawn_index = self.playerpos + (self.height - self.space_above_player) // TILE_SIZE_Y
            y = self.height + 120
            spawn_row = self.tiles[spawn_index]
            spawn_data = self.tile_data[spawn_index]
        else:
            y = -120
            spawn_index = self.playerpos - self.space_above_player // TILE_SIZE_Y
            spawn_row = self.tiles[spawn_index]
            spawn_data = self.tile_data[spawn_index]

        if "+" in spawn_row:
            return
        
        lane_width = (len(spawn_row) - 1) * ROAD_SIZE_X
        x_start = X_CENTRE - lane_width / 2
        
        valid_lanes = []
        desired_dir = driving_direction
        for lane_index, lane_data in spawn_data["lanes"].items():
            
            if lane_data["dir"] == desired_dir or lane_data["dir"] == "both":
                lane_x = self.lane_to_x(x_start, lane_index)
                
                if not self.lane_clear(lane_index, y):
                    continue
                if not lane_x:
                    continue

                valid_lanes.append({
                    "x": lane_x,
                    "lane_index": lane_index,
                    "direction": lane_data["dir"],
                })

        if not valid_lanes:
            return
        lane = random.choice(valid_lanes)

        npc = Npc(self, image, lane["x"], y, npc_speed, lane["lane_index"], lane["direction"]) 
        self.npcs.add(npc)
        self.all_sprites.add(npc)

    def query_npcs(self, lane_index, direction=None):
        npcs = []
        for npc in self.npcs:
            if npc.lane_index != lane_index:
                continue

            if (direction is not None and npc.dir != direction):
                continue

            npcs.append(npc)
        return npcs

    def collisions(self):
        now = pygame.time.get_ticks()
        _, char = self.on_road()

        # invincibility timer
        if self.invincible:
            if now - self.flash_timer > self.flash_interval:
                self.player_opacity = 100 if self.player_opacity > 100 else 255
                self.flash_timer = now

            if now - self.invincible_time > self.spawncamp_delay:
                self.invincible = False
                self.player_opacity = 255

        print(char, self.running_red(char), self.tiler.signals(), self.tile_data[round(self.playerpos + SPACE_ABOVE_PLAYER // TILE_SIZE_Y)]["layout"])
        if self.running_red(char):
            if self.chased == False:
                print("[!!!POLICE SIREN SOUNDS!!!]")
                self.spawn_police()
                self.chased = True
            else:
                pass

        for enemy in self.enemies:
            if SPACE_ABOVE_PLAYER - CATCH_DISTANCE < enemy.world_y:
                self.gaming = False
                return

        # NPC collision
        for npc in self.npcs:
            if not self.player_hitbox:
                continue
            if self.player_hitbox.colliderect(npc.hitbox):
                self.oof()
                return  # IMPORTANT: prevent double damage same frame

        # road check
        if self.out_of_bounds(char):
            print("OUCH")
            self.oof()
        
    def oof(self):
        if self.invincible:
            return

        self.health -= 1
        print("CRASH")
        print("Health:", self.health)

        self.invincible = True
        now = pygame.time.get_ticks()
        self.invincible_time = now
        self.flash_timer = now

        if self.health <= 0:
            print("game over")

    def out_of_bounds(self, char):
        if char == "OOB" or char == "S":
            return True
        else:
            return False
        
    def running_red(self, char):
        self.signal, self.signaltimer = self.tiler.signals()
        if (char == "+" or char == "`" or char == "%") and self.signal:
            return True
        else:
            return False
        
    def spawn_police(self):
        if self.chased == False:
            self.chased = True
            popo = Police(
                self,
                self.assets.get_image("policecar1"),
                X_CENTRE,
                -100,
                MAX_SPEED // 0.8,
                0,
                "down"
            )
            self.enemies.add(popo)
            self.all_sprites.add(popo)
            self.vlc("police", 1, True)
        else:
            pass
                
            
    def on_road(self):
        row = self.tile_data[round(self.playerpos + SPACE_ABOVE_PLAYER // TILE_SIZE_Y)]["layout"]
        print(row)
        lane_width = ((len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X))
        x_start = X_CENTRE - lane_width / 2

        lane_index = round((self.player_x - x_start) / ROAD_SIZE_X)

        char = row[lane_index] if 0 <= lane_index < len(row) else 'OOB'
        return (
            0 <= lane_index < len(row)
            and row[lane_index] == ".",
            char
        )
    
    def get_player_corners(self):
        return (
            self.player_rect.topleft, 
            self.player_rect.topright, 
            self.player_rect.bottomleft, 
            self.player_rect.bottomright
        )

    def lane_clear(self, lane_index, y, min_distance=250):
        for npc in self.npcs:
            if npc.lane_index != lane_index:
                continue
            if abs(npc.world_y - y) < min_distance:
                return False
        return True
    
    def closest_lane(self):

        current_row = self.tile_data[self.playerpos]
        row = self.tiles[self.playerpos]

        lane_width = ((len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X))
        x_start = X_CENTRE - lane_width / 2

        closest_lane = None
        closest_distance = float("inf")

        for lane_index in current_row["lanes"]:

            lane_x = self.lane_to_x(x_start, lane_index)
            distance = abs(lane_x - self.player_x)

            if distance < closest_distance:
                closest_distance = distance
                closest_lane = lane_index

        return closest_lane
    
    def lane_offset(self):
        lane = self.closest_lane()
        current_row = self.tile_data[self.playerpos]
        row = self.tiles[self.playerpos]

        lane_width = ((len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X))
        x_start = X_CENTRE - lane_width / 2

        lane_x = self.lane_to_x(x_start, lane)
        return self.player_x - lane_x

    def scenery_generator(self, biome="grassland"):
        """Carey this is for you, I want this function to generate random scenery"""
        scenery = []

        biome = self.current_biome
        data = BIOMES[biome]

        if type == "tree":
            count = int(1000 * 600 * data["tree_density"] * 0.00005)

            tree_images = [
                img for img in data["backround_images"]
                if "tree" in img 
            ]
        
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
            for i in range(int(HEIGHT // ROAD_SIZE_X)):
                pattern_key = pattern_key + (str(random.randrange(1, NUM_WEATHERING_PATTERNS)))
            return pattern_key
        
        # else:
        #     # R = road
        #     # L = white line
        #     # Y = yellow line
        #     # _ = placeholder
        #     if self.playerpos < 10:
        #         return "__S|.|.|S__"
        #     elif self.playerpos < 20:
        #         return "SC./.|./.CS"
        #     elif self.corner_test:
        #         self.corner_test = False
        #         return "1-./.|./.-2"
        #     else:
        #         return "_-./.|./.C_"

    def bg_tiler(self):
        """Generates a text file which represents the road that gets sent to bg_blitter"""
        self.scroll_offset -= self.playerspeed * self.dt
        while self.scroll_offset < 0:
            self.scroll_offset += TILE_SIZE_Y

            self.playerpos += 1

            row = self.tiler.next_row()
            self.tiles.append(row["layout"])
            self.tile_data.append(row)
            self.weathering.append(
                self.bg_generator("weathering")
            )

        while self.scroll_offset >= TILE_SIZE_Y:
            self.scroll_offset -= TILE_SIZE_Y
            self.playerpos = max(0, self.playerpos - 1)

    def bg_tiler_init(self):
        rows_needed = HEIGHT // TILE_SIZE_Y + 5
        for _ in range(rows_needed):
            row = self.tiler.next_row()

            self.tiles.append(row["layout"])
            self.tile_data.append(row)
            self.weathering.append(self.bg_generator("weathering"))
        if DEBUG:
            print(self.weathering)

    def bg_blitter(self):
        """Renders the text from bg_tiler into road images"""
        rows_visible = HEIGHT // TILE_SIZE_Y + 3
        start_row = max(0, self.playerpos - rows_visible)
        end_row = self.playerpos + rows_visible
        signalimg = None
        
        for row_index in range(start_row, end_row):
            row = self.tiles[row_index]
            # print("row", row)
            distance_from_player = row_index - self.playerpos
            # print("distance from player", distance_from_player)
            y = row_index * TILE_SIZE_Y - self.playerpos * TILE_SIZE_Y + self.scroll_offset
            # print("Y", y)
            road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X)
            x_start = X_CENTRE - road_width / 2
            #half_road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X) + LINE_SIZE_X * 2
            
            for col_index, char in enumerate(row):
                if char == "." or char == "," or char == "+":
                    img = self.assets.get_image("road_tile")
                    weathering = self.assets.get_image("weathered_pattern_" + self.weathering[row_index][col_index // 2])

                elif char == "S":
                    img = self.assets.get_image("sidewalk_tile")
                
                elif char == "C":
                    img = self.assets.get_image("curb")
                
                elif char == "-" or char == "`":
                    img = self.assets.get_image("no_road_line")

                elif char == ":":
                    img = self.assets.get_image("white_dashed_road_line")

                elif char == ";":
                    img = self.assets.get_image("yellow_dashed_road_line")

                elif char == "|":
                    img = self.assets.get_image("white_solid_road_line")

                elif char == "/":
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

                elif char == "5":
                    img = self.assets.get_image("UL_concrete_merge")
                
                elif char == "6":
                    img = self.assets.get_image("UR_concrete_merge")
                
                elif char == "7":
                    img = self.assets.get_image("DL_concrete_merge")
                
                elif char == "8":
                    img = self.assets.get_image("DR_concrete_merge")

                elif char == "a":
                    img = self.assets.get_image("UL_corner")

                elif char == "s":
                    img = self.assets.get_image("UR_corner")

                elif char == "d":
                    img = self.assets.get_image("DL_corner")
                
                elif char == "f":
                    img = self.assets.get_image("DR_corner")
                
                elif char == "%":
                    if self.signal:
                        if self.signaltimer < 1:
                            signalimg = self.assets.get_image("RY_light")
                        else:
                            signalimg = self.assets.get_image("R_light")

                    else:
                        if self.signaltimer < 1:
                            signalimg = self.assets.get_image("Y_light")
                        else:
                            signalimg = self.assets.get_image("G_light")
                    
                    signalrect = signalimg.get_rect()
                    signalrect.center = (x_start + ROAD_SIZE_X * col_index, y)
                    continue

                else:
                    continue
                
                img_rect = img.get_rect()
                img_rect.center = (x_start + ROAD_SIZE_X * col_index, y)

                self.screen.blit(img, img_rect)
                if char == ".":
                    self.screen.blit(weathering, img_rect)
                if char == "S":
                    pass

        if signalimg:
            self.screen.blit(signalimg, signalrect)

    def vlc(self, music, times=-1, overwrite=True):
        if self.music[0] == music:
            return
        if overwrite == True:
            self.music[0] = music
            pygame.mixer.music.load(
                self.assets.get_music(self.music[0])
            )
            pygame.mixer.music.play(times)
            self.music[1] = True
        else:
            if self.music[1] == False:
                self.music[0] = music
                pygame.mixer.music.load(
                    self.assets.get_music(self.music[0])
                )
                pygame.mixer.music.play(times)
                self.music[1] = False
            else:
                return
            
    def sfx(self, sfx, id=None):
        if self.sound[0] == sfx:
            return
        if self.sound[1] == id:
            return
        self.sound[0] = sfx
        self.sound[1] = id
        self.assets.get_sound(sfx).play()
        
    def gametime(self):
        minutes, seconds = divmod(int(self.igt), 60)
        return f"8:{minutes:02d}:{seconds:02d}am"

    def lane_to_x(self, x_start, lane_index):
        return x_start + lane_index * ROAD_SIZE_X
    
    def x_to_lane(self, x, x_start):
        return round((x - x_start) / ROAD_SIZE_X)

    def show_actions(self):
        tutorial_img = self.assets.get_image("tutorial")
        tutorial_rect = tutorial_img.get_rect(center=(X_CENTRE, HEIGHT - 200))
        if self.t % 0.5 < 0.35:
            self.screen.blit(tutorial_img, tutorial_rect)

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
