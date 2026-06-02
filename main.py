import pygame
import random
from settings import *
from systems.asset_loader import AssetLoader
from levels.traffic import Tiler
from levels.biomes import BIOMES
from levels.roads import ROAD_TYPES
from entities.npc import Npc

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = WIDTH
        self.height = HEIGHT
        self.space_above_player = SPACE_ABOVE_PLAYER
        self.all_sprites = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        random.seed(SEED)
        self.tiler = Tiler(
            seed=SEED,
            driving_side="right" if NOT_BRITISH_DRIVING else "left"
        )
        print(SEED)
        self.not_british_driving = NOT_BRITISH_DRIVING

        # Run AssetLoader and save it in self.assets
        self.assets = AssetLoader()
        self.assets.load_images()
        self.assets.load_music()

        self.car_options = self.assets.car_models
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
        
        # Utils
        self.t = 0
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

        if DEBUG or not(DEBUG):
            self.corner_test = True

    def run(self):
        self.vlc("menu")
        self.select_car_menu()
        self.vlc("theme")
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
        print(self.tiles)

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
        if random.random() < traffic_density * self.dt * (self.playerspeed / MAX_SPEED + 0.5):
            self.spawn_npc()
        self.all_sprites.update(self.dt)
        self.collisions()

    def draw(self):
        self.screen.fill((100, 100, 100))
        self.bg_blitter()
        self.all_sprites.draw(self.screen)  

        self.player_img.set_alpha(self.player_opacity)
        angle = self.player_vx * 0.05
        player_rotated = pygame.transform.rotate(self.player_img, angle + 180)
        rect = player_rotated.get_rect(
            center=(self.player_x, self.player_y)
        )
        self.player_rect = rect
        self.screen.blit(player_rotated, rect)    

        for i in range(self.health):
            self.screen.blit(self.star_img, (20 + i * 40, 20))

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

        # invincibility timer
        if self.invincible:
            if now - self.flash_timer > self.flash_interval:
                self.player_opacity = 100 if self.player_opacity > 100 else 255
                self.flash_timer = now

            if now - self.invincible_time > self.spawncamp_delay:
                self.invincible = False

        # NPC collision
        for npc in self.npcs:
            if self.player_rect.colliderect(npc.rect):
                self.oof()
                return  # IMPORTANT: prevent double damage same frame

        # road check
        if self.out_of_bounds():
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
            print("GAME OVER")

    def out_of_bounds(self):
        _, char = self.on_road()
        print("char", char)
        if char == "OOB" or char == "S":
            print("OOF")
            return True
        else:
            return False

    def is_lane_in_bounds(self, road_data, lane_index):
        return lane_index in road_data["bounds"]
    
    def on_road(self):

        row = self.tile_data[self.playerpos]["layout"]

        lane_width = ((len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X))
        x_start = X_CENTRE - lane_width / 2

        lane_index = round((self.player_x - x_start) / ROAD_SIZE_X)

        char = row[lane_index] if 0 <= lane_index < len(row) else 'OOB'
        print(char)
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
            if self.playerpos < 10:
                return "__S|.|.|S__"
            elif self.playerpos < 20:
                return "SC./.|./.CS"
            elif self.corner_test:
                self.corner_test = False
                return "1-./.|./.-2"
            else:
                return "_-./.|./.C_"

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
                if char == ".":
                    img = self.assets.get_image("road_tile")
                    weathering = self.assets.get_image("weathered_pattern_" + self.weathering[row_index][col_index // 2])

                elif char == "S":
                    img = self.assets.get_image("sidewalk_tile")
                
                elif char == "C":
                    img = self.assets.get_image("curb")
                
                elif char == "-":
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
                
                else:
                    continue
                
                img_rect = img.get_rect()
                img_rect.center = (x_start + ROAD_SIZE_X * col_index, y)

                self.screen.blit(img, img_rect)
                if char == ".":
                    self.screen.blit(weathering, img_rect)
                if char == "S":
                    pass

    def select_car_menu(self):
        selecting = True
        font = pygame.font.SysFont("Arial", 40, bold=True)
        
        card_w, card_h = 160, 190  
        spacing_x, spacing_y = 30, 60
        
        row1_count = 5
        row1_start_x = X_CENTRE - ((card_w * row1_count + spacing_x * (row1_count - 1)) / 2)
        row1_y = Y_CENTRE - card_h - (spacing_y / 2)
     
        row2_count = 4
        row2_start_x = X_CENTRE - ((card_w * row2_count + spacing_x * (row2_count - 1)) / 2)
        row2_y = Y_CENTRE + (spacing_y / 2)

        rects = []
        for idx in range(len(self.car_options)):
            if idx < 5:
                x = row1_start_x + idx * (card_w + spacing_x)
                y = row1_y
            else:
                x = row2_start_x + (idx - 5) * (card_w + spacing_x)
                y = row2_y
            rects.append(pygame.Rect(x, y, card_w, card_h))

        exit_btn_w, exit_btn_h = 160, 50
        exit_btn_rect = pygame.Rect(20, HEIGHT - 20 - exit_btn_h, exit_btn_w, exit_btn_h)
        exit_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        stats_btn_w, stats_btn_h = 160, 50
        stats_btn_rect = pygame.Rect(X_CENTRE - stats_btn_w / 2, HEIGHT - 20 - stats_btn_h, stats_btn_w, stats_btn_h)
        stats_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        car_name_font = pygame.font.SysFont("Arial", 18, bold=True)

        while selecting:
            self.screen.fill("#1B1B1B")
            
            welcome_font = pygame.font.SysFont("Arial", 70, bold=True) 
            welcome_surf = welcome_font.render("WELCOME TO GTA 6", True, (255, 215, 0)) 
            welcome_rect = welcome_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 0.8))
            self.screen.blit(welcome_surf, welcome_rect)
            
            title_surf = font.render("PICK YOUR RIDE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 1.5))
            self.screen.blit(title_surf, title_rect)

            footer_font = pygame.font.SysFont("Arial", 16, bold=False)
            footer_surf1 = footer_font.render("v1.0.0 Alpha", True, (120, 120, 125)) 
            footer_rect1 = footer_surf1.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
            footer_surf2 = footer_font.render("Developed by Aiden, Tristan, and Carey", True, (120, 120, 125))
            footer_rect2 = footer_surf2.get_rect(bottomright=footer_rect1.topright)
            self.screen.blit(footer_surf1, footer_rect1)
            self.screen.blit(footer_surf2, footer_rect2)

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    for idx, rect in enumerate(rects):
                        if rect.collidepoint(click_pos):
                            chosen_key = self.car_options[idx]
                            self.player_model = chosen_key
                            self.player_img = self.assets.get_image(chosen_key)
                            selecting = False
                    
                    if exit_btn_rect.collidepoint(click_pos):
                        pygame.quit()
                        import sys
                        sys.exit()
                        
                    if stats_btn_rect.collidepoint(click_pos):
                        self.stats_menu()
            
            for idx, rect in enumerate(rects):
                if rect.collidepoint(mouse_pos):
                    color = (0, 200, 100)
                    border = 5
                else:
                    color = (180, 180, 180)
                    border = 2
                
                pygame.draw.rect(self.screen, color, rect, border, border_radius=12)
                
                car_surface = self.assets.get_image(self.car_options[idx])
                car_rect = car_surface.get_rect(center=(rect.centerx, rect.centery - 15))
                self.screen.blit(car_surface, car_rect)
                
                raw_name = self.car_options[idx]
                clean_name = raw_name.replace("_", " ").title()
                
                name_surf = car_name_font.render(clean_name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(rect.centerx, rect.bottom - 20))
                self.screen.blit(name_surf, name_rect)

            if exit_btn_rect.collidepoint(mouse_pos):
                exit_bg_color = (130, 20, 20)
                exit_border_width = 0
            else:
                exit_bg_color = (200, 50, 50)
                exit_border_width = 2
                
            pygame.draw.rect(self.screen, exit_bg_color, exit_btn_rect, exit_border_width, border_radius=6)
            
            exit_text_surf = exit_font.render("EXIT GAME", True, (255, 255, 255))
            exit_text_rect = exit_text_surf.get_rect(center=exit_btn_rect.center)
            self.screen.blit(exit_text_surf, exit_text_rect)

            if stats_btn_rect.collidepoint(mouse_pos):
                stats_bg_color = (20, 100, 130)
                stats_border_width = 0
            else:
                stats_bg_color = (50, 150, 200)
                stats_border_width = 2
                
            pygame.draw.rect(self.screen, stats_bg_color, stats_btn_rect, stats_border_width, border_radius=6)
            
            stats_text_surf = stats_font.render("STATS", True, (255, 255, 255))
            stats_text_rect = stats_text_surf.get_rect(center=stats_btn_rect.center)
            self.screen.blit(stats_text_surf, stats_text_rect)

            pygame.display.flip()
            self.clock.tick(30)

    def stats_menu(self):
        viewing_stats = True
        title_font = pygame.font.SysFont("Arial", 60, bold=True)
        content_font = pygame.font.SysFont("Arial", 30, bold=False)
        back_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        back_btn_w, back_btn_h = 160, 50
        back_btn_rect = pygame.Rect(20, HEIGHT - 20 - back_btn_h, back_btn_w, back_btn_h)
        
        while viewing_stats:
            self.screen.fill("#2c3e50") 
            
            title_surf = title_font.render("VEHICLE STATS", True, (255, 215, 0))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 6))
            self.screen.blit(title_surf, title_rect)
            
            demo_surf = content_font.render("Stats details page coming soon...", True, (255, 255, 255))
            demo_rect = demo_surf.get_rect(center=(X_CENTRE, Y_CENTRE))
            self.screen.blit(demo_surf, demo_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn_rect.collidepoint(event.pos):
                        viewing_stats = False 
            
            if back_btn_rect.collidepoint(mouse_pos):
                back_bg_color = (180, 180, 180)
                back_border_width = 0
            else:
                back_bg_color = (100, 110, 120)
                back_border_width = 2
                
            pygame.draw.rect(self.screen, back_bg_color, back_btn_rect, back_border_width, border_radius=6)
            
            back_text_surf = back_font.render("BACK", True, (255, 255, 255))
            back_text_rect = back_text_surf.get_rect(center=back_btn_rect.center)
            self.screen.blit(back_text_surf, back_text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)

    def vlc(self, music):
        pygame.mixer.music.load(
            self.assets.get_music(music)
        )
        pygame.mixer.music.play(-1)
    
    def lane_to_x(self, x_start, lane_index):
        return x_start + lane_index * ROAD_SIZE_X
    
    def x_to_lane(self, x, x_start):
        return round((x - x_start) / ROAD_SIZE_X)

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