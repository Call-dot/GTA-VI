import pygame
import random
from settings import *
from saves import save_run
from systems.asset_loader import AssetLoader
from levels.traffic import Tiler
from levels.nature import Nature
from levels.biomes import BIOMES
from levels.roads import ROAD_TYPES
from entities.npc import Npc
from entities.enemy import Police
from systems.ui import Ui
from systems.powerups import *

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
        self.seed = random.randrange(2147483647)
        random.seed(self.seed)
        self.tiler = Tiler(
            self,
            seed=self.seed,
            driving_side="right" if NOT_BRITISH_DRIVING else "left"
        )
        self.nature = Nature(
            self,
            seed=self.seed
        )
        print(self.seed)
        self.not_british_driving = NOT_BRITISH_DRIVING
        self.igt = 0
        self.success = False
        self.respect = False

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

        self.playermode = 0
        self.playerspeed = 0
        self.playerdir = 0
        self.playerpos = 0

        self.player_x = X_CENTRE
        self.player_y = HEIGHT - SPACE_ABOVE_PLAYER
        self.player_vx = 0
        self.player_rect = None
        self.player_hitbox = None
        self.playerangle = 0
        self.playerjump = False
        
        # Utils
        self.tiles = []
        self.tile_data = []
        self.weathering = []
        self.trees = []
        self.rocks = []
        self.scroll_offset = 0
        self.x_offset = 0
        self.ts_down = 0
        self.current_biome = "badlands"
        self.bg_tiler_init()

        self.health = 5
        self.flash_timer = 0
        self.flash_interval = 150  # milliseconds
        self.player_opacity = 255
        self.invincible = False
        self.invincible_time = 0
        self.spawncamp_delay = SPAWNCAMP_DELAY  # milliseconds
        self.endpoint = None
        self.signal = True
        self.signaltimer = 0
        self.music = [None, False]
        self.sound = [None, None]
        self.chased = False
        self.tutorial = True
        self.inventory = None
        self.stealing = False
        self.speeding = False
        self.speeding_timer  = 0.0

        if DEBUG or not(DEBUG):
            self.corner_test = True

    def new_game(self):
        self.playeropacity = 255
        self.health = 5
        self.playerspeed = 0
        self.playerpos = 0
        self.chased = False
        self.igt = 0
        self.endpoint = None
        self.success = False
        self.respect = False

        self.player_x = X_CENTRE
        self.player_y = HEIGHT - SPACE_ABOVE_PLAYER
        self.player_vx = 0
        self.player_rect = None
        self.player_hitbox = None
        self.playerjump = False
        self.jump_timer = 0.0
        self.playerangle = 0
        self.tutorial = True
        self.tiler.almost_there = False
        self.inventory = None
        self.speeding = False
        self.speeding_timer = 0.0

        self.npcs.empty()
        self.enemies.empty()
        self.all_sprites.empty()

        self.tiles.clear()
        self.tile_data.clear()
        self.weathering.clear()
        self.trees.clear() 
        self.rocks.clear() 
        self.tiler.choose_new_road()
        self.tiler.intersection.clear()

        self.bg_tiler_init()
    
    def new_run(self):
        self.ui.startup()
        while True:
            if not self.ui.main_menu():
                return
            if self.ui.select_car_menu():
                break

        self.gaming = True
        self.ui.intro_screen()

    def end_run(self):
        if self.success:
            self.respect = self.ui.outro_screen(self.igt)
        else:
            self.respect = False

        save_run(self)

        self.ui.ending(self.respect)
        print(self.tiles)
        self.player_opacity = 255
        self.player_img.set_alpha(self.player_opacity)

    def run(self):
        self.ui.startup()
        while self.running:
            self.new_game()
            self.new_run()
            while self.gaming:
                self.vlc("theme", -1, False)
                self.dt = self.clock.tick(30) / 1000
                self.t += self.dt
                self.events()
                if not self.gaming:
                    break
                self.playerinput(self.dt)
                self.player()
                self.update()
                self.bg_tiler()
                self.draw()
            self.end_run()

    def events(self):
        # --- FIXED: Pause button click area bounding box shifted to the left edge ---
        pause_btn = pygame.Rect(20, 20, 40, 40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gaming = False
                self.running = False
                pygame.quit()
                import sys
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.t > 2:
                    self.tutorial = False
                
                if event.key == pygame.K_ESCAPE:
                    status = self.ui.pause_menu()
                    if status == "exit":
                        self.gaming = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos 
                print(f"Mouse Clicked at X: {mouse_x}, Y: {mouse_y}")

                if event.button == 1 and pause_btn.collidepoint(event.pos):
                    status = self.ui.pause_menu()
                    if status == "exit":
                        self.gaming = False

    def playerinput(self, dt):
        keys = pygame.key.get_pressed()
        self.playerjump = keys[pygame.K_SPACE]
        
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.playermode = 1 if not self.playerjump else 0
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.playermode = 2 if not self.playerjump else 0
        else:
            self.playermode = 0
    
        if (
            (keys[pygame.K_a] and not keys[pygame.K_d]) or
            (keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT])
        ):
            self.playerdir = 1
        elif (
            (keys[pygame.K_d] and not keys[pygame.K_a]) or
            (keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT])
        ):
            self.playerdir = 2
        else:
            self.playerdir = 0
        
        self.stealing = keys[pygame.K_q] or keys[pygame.K_LSHIFT]

        if keys[pygame.K_e] or keys[pygame.K_RSHIFT]:
            print(self.inventory)
            self.use_powerup()

    def accelerate(self):
        if self.speeding:
            acceleration = (ULTRA_SPEED - self.playerspeed) * 2
        else:
            acceleration = (MAX_SPEED - self.playerspeed) * 2
        self.playerspeed += acceleration * self.dt
        
    def decelerate(self, friction):
        deceleration = (0 - self.playerspeed) * friction
        self.playerspeed += deceleration * self.dt

    def reverse(self, friction):
        deceleration = (REVERSE_SPEED - self.playerspeed) * friction
        self.playerspeed += deceleration * self.dt
    
    def player(self):
        if self.playermode == 1:
            self.accelerate()
        elif self.playermode == 2:
            self.reverse(BRAKE_POWER)
        else:
            if self.playerjump:
                self.decelerate(AIR_RESISTANCE)
            else:
                self.decelerate(FRICTION)

        if not self.playerjump:
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
        if self.speeding:
            self.player_vx *= (self.playerspeed / ULTRA_SPEED)
        else:
            self.player_vx *= (self.playerspeed / MAX_SPEED)
        self.player_x += self.player_vx * self.dt
        
        if self.player_x > WIDTH+50:
            self.player_x = -40
        elif self.player_x < -50:
            self.player_x = WIDTH+40

        if not self.playerjump:
            self.jump_timer = 0
        else:
            if self.jump_timer <= 0:
                self.jump_timer = AIRTIME
            else:
                self.jump_timer = max(0, self.jump_timer - self.dt)

    def vibes(self, dt):
        pass

    def update(self):
        if self.playerpos > SCHOOL_DISTANCE:
            self.tiler.almost_there = True
        if self.endpoint and self.playerpos > self.endpoint:
            self.gaming = False
            self.success = True
        current_road = self.tile_data[self.playerpos]
        traffic_density = current_road["road_type"]["traffic"]
        self.igt += self.dt * TIMEWARP
        if random.random() < traffic_density * self.dt * (self.playerspeed / MAX_SPEED + 0.5):
            self.spawn_npc()
        self.all_sprites.update(self.dt)
        self.collisions()
        self.tick_powerups(self.dt)

    def draw(self):
        self.screen.fill(BIOMES[self.current_biome]["vibe"])
        print(self.trees, self.rocks)
        self.bg_blitter()
        self.all_sprites.draw(self.screen)  
        for npc in self.npcs:
            npc.draw_powerup_icon(self.screen)

        self.player_img.set_alpha(self.player_opacity)
        self.playerangle = self.player_vx * 0.05

        player_rotated = self.player_img
        if self.playerjump:
            og_width = player_rotated.get_width()
            og_height = player_rotated.get_height()
            inflation = -0.42 * self.jump_timer * (self.jump_timer - AIRTIME) + 1
            player_rotated = pygame.transform.smoothscale(player_rotated, (og_width*inflation, og_height*inflation))
        player_rotated = pygame.transform.rotate(player_rotated, self.playerangle + 180)
        rect = player_rotated.get_rect(
            center=(self.player_x, self.player_y)
        )
        hitbox = rect.inflate(-HITBOX_TOLERANCE, -HITBOX_TOLERANCE)
        print(self.playerjump, self.jump_timer)
        
        self.player_rect = rect
        self.player_hitbox = hitbox
        self.screen.blit(player_rotated, rect)    

        self.scenery_blitter()

        for i in range(self.health):
            self.screen.blit(self.star_img, (self.screen.get_width() - (69 + i * 40), 20))

        pause_btn = pygame.Rect(20, 20, 40, 40)
        mouse_pos = pygame.mouse.get_pos()
        pause_btn_color = (44, 62, 80) if pause_btn.collidepoint(mouse_pos) else (30, 43, 56)
        
        pygame.draw.rect(self.screen, pause_btn_color, pause_btn, border_radius=6)
        pygame.draw.rect(self.screen, (255, 215, 0), pause_btn, 1, border_radius=6)
        
        pygame.draw.line(self.screen, (255, 255, 255), (pause_btn.centerx - 4, pause_btn.top + 12), (pause_btn.centerx - 4, pause_btn.bottom - 12), 3)
        pygame.draw.line(self.screen, (255, 255, 255), (pause_btn.centerx + 4, pause_btn.top + 12), (pause_btn.centerx + 4, pause_btn.bottom - 12), 3)

        if self.inventory:
            powerup = POWERUP_TYPES.get(self.inventory)
            powerup_img = self.assets.get_image(powerup["icon"])
            # Push powerup layout down slightly to prevent clipping under the left-side pause button
            powerup_rect = powerup_img.get_rect(topleft=(20, 75))
            self.screen.blit(powerup_img, powerup_rect)
            
        clock_surf = self.fonts["highlight"].render(self.gametime(), True, ("#FEFEFE"))
        clock_rect = clock_surf.get_rect(topright=(self.screen.get_width()-20, 69))
        self.screen.blit(clock_surf, clock_rect)
        half_width = rect.width / 2

        pygame.draw.rect(self.screen, "Green", (self.screen.get_width() // 2 + 300, self.screen.get_height() // 2 - 300 + self.playerspeed, 167, 169)) 
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

        if self.endpoint:
            fade_start = self.endpoint - (END_THRESHOLD // 3)
            if self.playerpos >= fade_start:
                fadefactor = (
                    (self.playerpos - fade_start)
                    / (self.endpoint - fade_start)
                )
                fadefactor = min(max(fadefactor, 0), 1)
                fadeout_surf = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
                fadeout_surf.fill((200, 200, 200, int(fadefactor * 255)))
                self.screen.blit(fadeout_surf, (0, 0))

        if self.tutorial:
            self.show_actions()
        pygame.display.flip()

    def spawn_npc(self):
        _, image = self.assets.get_random_car(self.player_model)
        driving_direction = random.choice(["down", "up"])
        if driving_direction == "down":
            npc_speed = 100 
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

        if "+" in spawn_row or "9" in spawn_row or "0" in spawn_row:
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
                if not lane_data["allow_spawn"]:
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

        if self.invincible:
            if now - self.flash_timer > self.flash_interval:
                self.player_opacity = 100 if self.player_opacity > 100 else 255
                self.flash_timer = now

            if now - self.invincible_time > self.spawncamp_delay:
                self.invincible = False
                self.player_opacity = 255
        else:
            self.player_opacity = 255

        if self.running_red(char):
            if self.chased == False:
                print("[!!!POLICE SIREN SOUNDS!!!]")
                self.spawn_police()
                self.chased = True

        for enemy in self.enemies:
            for npc in self.npcs:
                if npc.hitbox and enemy.rect.colliderect(npc.hitbox):
                    npc.boom = {
                        "origin_x": enemy.world_x,
                        "origin_y": enemy.world_y
                    }

            if SPACE_ABOVE_PLAYER - CATCH_DISTANCE < enemy.world_y:
                self.sfx("kid_slap", 4)
                self.gaming = False
                return

        for npc in self.npcs:
            if not self.player_hitbox or not self.player_rect:
                continue
 
            if not self.playerjump:
                if npc.hitbox and self.player_hitbox.colliderect(npc.hitbox):
                    self.oof()
                    return  
 
            if self.stealing and self.player_rect.colliderect(npc.rect):
                stolen = npc.try_steal(self.player_rect)
                self.sfx("slip", 6)
                if stolen: 
                    self.inventory = stolen
                    print(f"[POWERUP] Stole: {stolen}")

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
            self.music[1] = False
            self.vlc("police", 1, True)
            
    def on_road(self):
        row = self.tile_data[round(self.playerpos + SPACE_ABOVE_PLAYER // TILE_SIZE_Y)]["layout"]
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
    
    def tick_powerups(self, dt):
        """Count down any active timed powerup effects."""
        if self.speeding:
            self.speeding_timer -= dt
            if self.speeding_timer <= 0:
                self.speeding = False
                self.speeding_timer  = 0.0
                self.on_speed_powerup_end()
    
    def use_powerup(self):
        if self.inventory is None:
            return
 
        powerup = self.inventory
        self.inventory = None   # consume it
 
        if powerup == "speed":
            self.activate_speed_powerup()
        elif powerup == "bomb":
            self.activate_bomb_powerup()

    def activate_speed_powerup(self):

        self.music[1] = False
        self.vlc("speed", -1, True)
        self.speeding = True
        self.speeding_timer  = SPEED_POWERUP_DURATION
        print("[POWERUP] Speed boost activated!")
 
    def on_speed_powerup_end(self):
        if self.playerspeed > MAX_SPEED:
            self.playerspeed = MAX_SPEED
        self.music[1] = False
        print("[POWERUP] Speed boost ended.")

    def activate_bomb_powerup(self):
        print(f"[POWERUP] Bomb! clearing radius={BLAST_RADIUS}px")
        self.sfx("boom", 5)
        to_kill = []
        for enemy in self.enemies:
            enemy.boom = {
                "origin_x": self.player_x,
                "origin_y": self.player_y
            }
        for npc in self.npcs:
            dx = npc.world_x - self.player_x
            dy = npc.world_y - self.player_y
            dist = (dx * dx + dy * dy) ** 0.5
            if dist <= BLAST_RADIUS:
                to_kill.append(npc)
 
        for npc in to_kill:
            npc.boom = {
                "origin_x": self.player_x,
                "origin_y": self.player_y
            }
 
        print(f"[POWERUP] Bomb removed {len(to_kill)} NPCs.")

    def scenery_blitter(self):
        """
        Mirrors bg_blitter() — renders trees and rocks only where there is
        no road tile beneath them.
        """
        rows_visible = HEIGHT // TILE_SIZE_Y + 3
        start_row = max(0, self.playerpos - rows_visible)
        end_row = self.playerpos + rows_visible

        def location_on_road(x, y):
            """Returns True if screen position (x, y) falls on a road tile."""
            row_index = int((y + self.playerpos * TILE_SIZE_Y - self.scroll_offset) / TILE_SIZE_Y)
            if row_index < start_row or row_index >= end_row:
                return True
            if row_index >= len(self.tiles):
                return False

            row = self.tiles[row_index]
            road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X)
            x_start = X_CENTRE - road_width / 2

            col_index = round((x - x_start) / ROAD_SIZE_X)
            if 0 <= col_index < len(row):
                char = row[col_index]
                # Any non-grass character counts as "road" — skip rendering scenery here
                return char not in ("_", " ")
            return False  # outside road bounds = grass = fine to render

        for obj in self.trees:
            if location_on_road(obj["x"], obj["y"]):
                continue
            img = self.assets.get_image(obj["image"])
            img_rect = img.get_rect(center=(obj["x"], obj["y"]-50))
            self.screen.blit(img, img_rect)

        for obj in self.rocks:
            if location_on_road(obj["x"], obj["y"]):
                continue
            img = self.assets.get_image(obj["image"])
            img_rect = img.get_rect(center=(obj["x"], obj["y"]-50))
            self.screen.blit(img, img_rect)

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
        self.nature.scenery_tiler()

        """Generates a text file which represents the road that gets sent to bg_blitter"""
        self.scroll_offset -= self.playerspeed * self.dt

        while self.scroll_offset < 0:
            self.scroll_offset += TILE_SIZE_Y

            self.playerpos += 1

            row = self.tiler.next_row()
            self.tiles.append(row["layout"])
            self.tile_data.append(row)
            self.weathering.append(self.bg_generator("weathering"))

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
            
        self.trees = self.nature.scenery_generator("tree")
        self.rocks = self.nature.scenery_generator("rocks")

    def bg_blitter(self, tiles=None):
        """Renders the text from bg_tiler into road images"""
        rows_visible = HEIGHT // TILE_SIZE_Y + 3
        start_row = max(0, self.playerpos - rows_visible)
        end_row = self.playerpos + rows_visible
        signalimg = None
        
        for row_index in range(start_row, end_row):
            row = tiles[row_index] if tiles else self.tiles[row_index]
            # print("row", row)
            # distance_from_player = row_index - self.playerpos
            # print("distance from player", distance_from_player)
            y = row_index * TILE_SIZE_Y - self.playerpos * TILE_SIZE_Y + self.scroll_offset
            # print("Y", y)
            road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X)
            x_start = X_CENTRE - road_width / 2
            #half_road_width = (len(row) - 1) / 2 * (TILE_SIZE_X + LINE_SIZE_X) + LINE_SIZE_X * 2
            
            for col_index, char in enumerate(row):
                if char == "." or char == "," or char == "+" or char == "$":
                    img = self.assets.get_image("road_tile")
                    weathering = self.assets.get_image("weathered_pattern_" + self.weathering[row_index][col_index // 2])

                elif char == "S":
                    img = self.assets.get_image("sidewalk_tile")

                elif char == "9":
                    img = self.assets.get_image("U_sideroad_sidewalk")

                elif char == "0":
                    img = self.assets.get_image("D_sideroad_sidewalk")
                
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

                elif char == "@":
                    img = self.assets.get_image("school_sign")
                
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
        if self.sound[0] == sfx and self.sound[1] == id:
            return
        self.sound[0] = sfx
        self.sound[1] = id
        print(self.sound)
        self.assets.get_sound(sfx).play()
        
    def gametime(self):
        total_seconds = int(self.igt) + DEPARTURE_TIME
        total_minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}am"

    def lane_to_x(self, x_start, lane_index):
        return x_start + int(lane_index) * ROAD_SIZE_X
    
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
