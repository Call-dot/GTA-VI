import pygame
import random
import math
#from systems.asset_loader import AssetLoader
from settings import *
from entities.npc import Npc

class Ui:
    def __init__(self, game):
        self.game = game
        self.assets = game.assets
        self.fonts = {
            "title": self.assets.get_font("honk"),
            "subtitle": self.assets.get_font("pixelify"),
            "header": self.assets.get_font("ops"),
            "body": self.assets.get_font("bungee"),
            "highlight": self.assets.get_font("rubik"),
            "caption": self.assets.get_font("tiny")
        }

    def startup(self):
        t = 0
        pygame.mixer.music.stop()
        while t < 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            self.game.screen.fill("#1B1B1B")
            logo = self.assets.get_image("strockstar")
            logo_rect = logo.get_rect(center=(X_CENTRE, Y_CENTRE))
            self.game.screen.blit(logo, logo_rect)
            pygame.display.flip()
            dt = self.game.clock.tick(30) / 1000
            t += dt

    def intro_screen(self):
        t = 0
        pygame.mixer.music.stop()
        while t < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            self.game.screen.fill("#1B1B1B")
            mission_surf1 = self.fonts["body"].render("Somewhere near St. Robert CHS", True, ("#FEFEFE"))
            mission_rect1 = mission_surf1.get_rect(center=(X_CENTRE, Y_CENTRE-100))
            mission_surf2 = self.fonts["body"].render("Don't be late for school!", True, ("#FEFEFE"))
            mission_rect2 = mission_surf2.get_rect(center=(X_CENTRE, Y_CENTRE))
            clock_surf = self.fonts["highlight"].render(self.game.gametime(), True, ("#FEFEFE"))
            clock_rect = clock_surf.get_rect(center=(X_CENTRE, Y_CENTRE+100))
            self.game.screen.blit(mission_surf1, mission_rect1)
            if t < 1:
                self.game.sfx("slap", 1)
            if t > 1:
                if t < 2:
                    self.game.sfx("slap", 3)
                self.game.screen.blit(mission_surf2, mission_rect2)
            if t > 2:
                self.game.sfx("slap", 2)
                self.game.screen.blit(clock_surf, clock_rect)
            pygame.display.flip()
            dt = self.game.clock.tick(30) / 1000
            t += dt

    def outro_screen(self, igt):
        t = 0
        finaletime = igt
        finale = True
        outing = True
        self.game.playerpos = 0
        self.game.playerspeed = 100
        player_img = self.game.player_img
        queue = int(finaletime * QUEUE_INTENSITY)
        npcs = []
        pygame.mixer.music.stop()
        tiles = ["4C5-,:,-6C3", "__SC,:,:,:,CS_@"]
        tiles.extend(["SC+:+:+:+CS" if i % 2 else "SC$:+:+:$CS" for i in range(queue)])
        tiles.extend(["______SC+:+:+:+-2999999", "______SC+`+`+`+`+`+`+`+", "______SC+`+`+`+`+`+`+`+", "______SC+`+`+`+`+`+`+`+", "______SC+:+:+:+-4000000"])
        tiles.extend(["SC$:+:+:$CS" for _ in range(25)])

        for row_idx, row in enumerate(tiles):
            for col_idx, char in enumerate(row):
                if char != "$":
                    continue

                _, image = self.assets.get_random_car(
                    self.game.player_model
                )

                road_width = (len(row) - 1) * ROAD_SIZE_X
                x_start = X_CENTRE - road_width / 2

                npcs.append({
                    "image": image,

                    # world coordinates
                    "world_row": row_idx,
                    "world_y": row_idx * TILE_SIZE_Y,

                    "world_x": x_start + col_idx * ROAD_SIZE_X,

                    "turning": False,
                    "turn_progress": 0.0,
                    "angle": 180,
                })
        intersection_row = None
        for row_idx, row in enumerate(tiles):
            if "2999999" in row:
                intersection_row = row_idx
                break
        
        while finale:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            dt = self.game.clock.tick(30) / 1000
            t += dt
            self.game.igt += dt * QUEUE_TIMEWARP
            self.game.screen.fill("#1B1B1B")
            if t > 2:
                self.game.playerspeed = 100
            while self.game.scroll_offset < 0:
                self.game.scroll_offset += TILE_SIZE_Y
                self.game.playerpos += 1
                self.game.weathering.append(
                    self.game.bg_generator("weathering")
                )
            self.game.scroll_offset -= self.game.playerspeed * dt
            self.game.bg_blitter(tiles)
            if t < 2:
                player_y = t * TILE_SIZE_Y
                player_x = ROAD_SIZE_X * 2 * math.sin(player_y * math.pi / (4 * TILE_SIZE_Y)) + X_CENTRE + ROAD_SIZE_X
                playerangle = math.sin(player_y * math.pi * 2 / (4 * TILE_SIZE_Y)) * 30
                print(player_x)
                player_rotated = pygame.transform.rotate(player_img, playerangle + 180)
                rect = player_rotated.get_rect(
                    center=(player_x, player_y)
                )
                self.game.screen.blit(player_rotated, rect)
            else:
                player_y = 2 * TILE_SIZE_Y
                player_x = X_CENTRE + 3 * ROAD_SIZE_X
                player_rotated = pygame.transform.rotate(player_img, 180)
                rect = player_img.get_rect(
                    center=(player_x, player_y)
                )
                self.game.screen.blit(player_rotated, rect)

            intersection_screen_y = (
                intersection_row * TILE_SIZE_Y
                - self.game.playerpos * TILE_SIZE_Y
                + self.game.scroll_offset
            )
            intersection_rect = pygame.Rect(
                0,
                intersection_screen_y - TILE_SIZE_Y // 2,
                WIDTH,
                TILE_SIZE_Y
            )
            for npc in npcs:
                screen_y = (npc["world_y"] - self.game.playerpos * TILE_SIZE_Y + self.game.scroll_offset)
                screen_x = npc["world_x"]

                if not npc["turning"]:
                    npc_rect = npc["image"].get_rect(
                        center=(screen_x, screen_y)
                    )
                    if npc_rect.colliderect(intersection_rect):
                        npc["turning"] = True
                        npc["turn_start_x"] = npc["world_x"]
                        npc["turn_start_y"] = npc["world_y"]

                else:
                    npc["turn_progress"] += dt * 0.75
                    p = min(1.0, npc["turn_progress"])
                    radius = ROAD_SIZE_X * 2
                    npc["world_x"] = (
                        npc["turn_start_x"]
                        + radius * math.sin(p * math.pi / 2)
                    )
                    npc["world_y"] = (
                        npc["turn_start_y"]
                        + radius * (1 - math.cos(p * math.pi / 2))
                    )
                    npc["angle"] = 180 - 90 * p
            
            for npc in npcs:
                screen_y = (npc["world_y"] - self.game.playerpos * TILE_SIZE_Y + self.game.scroll_offset)
                screen_x = npc["world_x"]
                rotated = pygame.transform.rotate(npc["image"], npc["angle"])
                rect = rotated.get_rect(center=(screen_x, screen_y))

                self.game.screen.blit(rotated, rect)


            clock_surf = self.fonts["highlight"].render(self.game.gametime(), True, ("#FEFEFE"))
            clock_rect = clock_surf.get_rect(center=(X_CENTRE, Y_CENTRE))
            self.game.screen.blit(clock_surf, clock_rect)
            
            if t > 19:
                finale = False
            pygame.display.flip()
            

        while t < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
            self.game.screen.fill("#1B1B1B")
            mission_surf1 = self.fonts["body"].render("This is the outro screen", True, ("#FEFEFE"))
            mission_rect1 = mission_surf1.get_rect(center=(X_CENTRE, Y_CENTRE-100))
            mission_surf2 = self.fonts["body"].render("it will display flag pull, stats and win/loss", True, ("#FEFEFE"))
            mission_rect2 = mission_surf2.get_rect(center=(X_CENTRE, Y_CENTRE))
            clock_surf = self.fonts["highlight"].render(self.game.gametime(), True, ("#FEFEFE"))
            clock_rect = clock_surf.get_rect(center=(X_CENTRE, Y_CENTRE+100))
            self.game.screen.blit(mission_surf1, mission_rect1)
            if t < 1:
                self.game.sfx("slap", 1)
            if t > 1:
                if t < 2:
                    self.game.sfx("slap", 3)
                self.game.screen.blit(mission_surf2, mission_rect2)
            if t > 2:
                self.game.sfx("slap", 2)
                self.game.screen.blit(clock_surf, clock_rect)
            pygame.display.flip()
            dt = self.game.clock.tick(30) / 1000
            t += dt


    def confirm_exit_popup(self):
        """Displays a centered 'Are you sure?' confirmation dialog overlay."""
        confirming = True
        
        popup_w, popup_h = 400, 200
        popup_rect = pygame.Rect(X_CENTRE - popup_w // 2, Y_CENTRE - popup_h // 2, popup_w, popup_h)
        
        btn_w, btn_h = 120, 45
        yes_btn = pygame.Rect(popup_rect.centerx - btn_w - 20, popup_rect.bottom - btn_h - 30, btn_w, btn_h)
        no_btn = pygame.Rect(popup_rect.centerx + 20, popup_rect.bottom - btn_h - 30, btn_w, btn_h)
        
        while confirming:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_btn.collidepoint(event.pos):
                        pygame.quit()
                        import sys
                        sys.exit()
                    if no_btn.collidepoint(event.pos):
                        return False 
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.game.screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(self.game.screen, (34, 47, 62), popup_rect, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), popup_rect, 3, border_radius=12)
            
            msg_surf = self.fonts["highlight"].render("ARE YOU SURE?", True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(popup_rect.centerx, popup_rect.top + 45))
            self.game.screen.blit(msg_surf, msg_rect)
            
            yes_color = (200, 50, 50) if yes_btn.collidepoint(mouse_pos) else (140, 30, 30)
            no_color = (100, 110, 120) if no_btn.collidepoint(mouse_pos) else (60, 70, 80)
            
            pygame.draw.rect(self.game.screen, yes_color, yes_btn, border_radius=6)
            pygame.draw.rect(self.game.screen, no_color, no_btn, border_radius=6)
            
            yes_surf = self.fonts["body"].render("YES", True, (255, 255, 255))
            no_surf = self.fonts["body"].render("NO", True, (255, 255, 255))
            
            self.game.screen.blit(yes_surf, yes_surf.get_rect(center=yes_btn.center))
            self.game.screen.blit(no_surf, no_surf.get_rect(center=no_btn.center))
            
            pygame.display.flip()
            self.game.clock.tick(30)

    def select_car_menu(self):
        selecting = True
        
        card_w, card_h = 160, 190  
        spacing_x, spacing_y = 30, 60
        
        row1_count = 5
        row1_start_x = X_CENTRE - ((card_w * row1_count + spacing_x * (row1_count - 1)) / 2)
        row1_y = Y_CENTRE - card_h - (spacing_y / 2)
     
        row2_count = 4
        row2_start_x = X_CENTRE - ((card_w * row2_count + spacing_x * (row2_count - 1)) / 2)
        row2_y = Y_CENTRE + (spacing_y / 2)

        rects = []
        for idx in range(len(self.game.car_options)):
            if idx < 5:
                x = row1_start_x + idx * (card_w + spacing_x)
                y = row1_y
            else:
                x = row2_start_x + (idx - 5) * (card_w + spacing_x)
                y = row2_y
            rects.append(pygame.Rect(x, y, card_w, card_h))

        exit_btn_w, exit_btn_h = 160, 50
        exit_btn_rect = pygame.Rect(20, HEIGHT - 20 - exit_btn_h, exit_btn_w, exit_btn_h)
        
        stats_btn_w, stats_btn_h = 160, 50
        stats_btn_rect = pygame.Rect(X_CENTRE - stats_btn_w / 2, HEIGHT - 20 - stats_btn_h, stats_btn_w, stats_btn_h)
        stats_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        car_name_font = pygame.font.SysFont("Arial", 18, bold=True)

        while selecting:
            self.game.screen.fill("#1B1B1B")
            
            welcome_font = self.fonts["title"]
            welcome_surf = welcome_font.render("WELCOME TO GTA 6", True, (255, 215, 0)) 
            welcome_rect = welcome_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 0.8))
            self.game.screen.blit(welcome_surf, welcome_rect)
            
            header_font = self.fonts["header"]
            title_surf = header_font.render("PICK YOUR RIDE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 1.5))
            self.game.screen.blit(title_surf, title_rect)

            footer_font = self.fonts["caption"]
            footer_surf1 = footer_font.render("v1.0.0 Alpha", True, (120, 120, 125)) 
            footer_rect1 = footer_surf1.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
            footer_surf2 = footer_font.render("Developed by Aiden, Tristan, and Carey", True, (120, 120, 125))
            footer_rect2 = footer_surf2.get_rect(bottomright=footer_rect1.topright)
            self.game.screen.blit(footer_surf1, footer_rect1)
            self.game.screen.blit(footer_surf2, footer_rect2)

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
                            chosen_key = self.game.car_options[idx]
                            self.game.player_model = chosen_key
                            self.game.player_img = self.game.assets.get_image(chosen_key)
                            self.game.current_car_idx = idx 
                            self.game.gaming = True
                            selecting = False
                    
                    if exit_btn_rect.collidepoint(click_pos):
                        self.confirm_exit_popup()
                        
                    if stats_btn_rect.collidepoint(click_pos):
                        hovered_idx = 0
                        for idx, rect in enumerate(rects):
                            if rect.collidepoint(mouse_pos):
                                hovered_idx = idx
                        self.game.current_car_idx = hovered_idx
                        self.stats_menu()
            
            for idx, rect in enumerate(rects):
                if rect.collidepoint(mouse_pos):
                    color = (0, 200, 100)
                    border = 5
                else:
                    color = (180, 180, 180)
                    border = 2
                
                pygame.draw.rect(self.game.screen, color, rect, border, border_radius=12)
                
                car_surface = self.game.assets.get_image(self.game.car_options[idx])
                car_rect = car_surface.get_rect(center=(rect.centerx, rect.centery - 15))
                self.game.screen.blit(car_surface, car_rect)
                
                raw_name = self.game.car_options[idx]
                clean_name = raw_name.replace("_", " ").title()
                
                name_surf = car_name_font.render(clean_name, True, (255, 255, 255))
                name_rect = name_surf.get_rect(center=(rect.centerx, rect.bottom - 20))
                self.game.screen.blit(name_surf, name_rect)

            if exit_btn_rect.collidepoint(mouse_pos):
                exit_bg_color = (130, 20, 20)
                exit_border_width = 0
            else:
                exit_bg_color = (200, 50, 50)
                exit_border_width = 2
                
            pygame.draw.rect(self.game.screen, exit_bg_color, exit_btn_rect, exit_border_width, border_radius=6)
            
            exit_text_surf = self.fonts["highlight"].render("EXIT GAME", True, (255, 255, 255))
            exit_text_rect = exit_text_surf.get_rect(center=exit_btn_rect.center)
            self.game.screen.blit(exit_text_surf, exit_text_rect)

            if stats_btn_rect.collidepoint(mouse_pos):
                stats_bg_color = (20, 100, 130)
                stats_border_width = 0
            else:
                stats_bg_color = (50, 150, 200)
                stats_border_width = 2
                
            pygame.draw.rect(self.game.screen, stats_bg_color, stats_btn_rect, stats_border_width, border_radius=6)
            
            stats_text_surf = stats_font.render("STATS", True, (255, 255, 255))
            stats_text_rect = stats_text_surf.get_rect(center=stats_btn_rect.center)
            self.game.screen.blit(stats_text_surf, stats_text_rect)

            pygame.display.flip()
            self.game.clock.tick(30)

    def ending(self):
        print("ending")

    def stats_menu(self):
        viewing_stats = True
        title_font = pygame.font.SysFont("Arial", 45, bold=True)
        label_font = pygame.font.SysFont("Arial", 26, bold=True)
        value_font = pygame.font.SysFont("Arial", 22, bold=False)
        back_font = pygame.font.SysFont("Arial", 24, bold=True)
        grid_font = pygame.font.SysFont("Arial", 14, bold=True)
        
        WIDTH = self.game.screen.get_width()
        HEIGHT = self.game.screen.get_height()
        X_CENTRE = WIDTH // 2
        
        inspect_idx = getattr(self.game, 'current_car_idx', 0)
        
        spin_angle = 0.0
        spin_speed = 3.0  
        last_car_key = None
        
        back_btn = pygame.Rect(20, HEIGHT - 70, 160, 50)
        left_panel = pygame.Rect(40, HEIGHT // 5, WIDTH // 2 - 60, HEIGHT // 2 - 20)
        
        grid_rects = []
        grid_start_x = 40
        grid_start_y = left_panel.bottom + 20
        grid_item_w = (left_panel.width - 20) // 3
        grid_item_h = 35
        
        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                if idx < len(self.game.car_options):
                    bx = grid_start_x + c * (grid_item_w + 10)
                    by = grid_start_y + r * (grid_item_h + 8)
                    grid_rects.append((idx, pygame.Rect(bx, by, grid_item_w, grid_item_h)))

        stats_x = WIDTH // 2 + 40
        stats_y = HEIGHT // 5 + 10
        row_gap = 75
        bar_max_w = 260
        bar_h = 16

        while viewing_stats:
            self.game.screen.fill("#1a252f") 
            mouse_pos = pygame.mouse.get_pos()
            
            car_key = self.game.car_options[inspect_idx]
            clean_name = car_key.replace("_", " ").title()
            
            if car_key != last_car_key:
                spin_angle = 0.0
                last_car_key = car_key
            
            spin_angle = (spin_angle + spin_speed) % 360.0
            
            car_stats = getattr(self.game, 'car_stats_database', {}).get(car_key, {"speed": 50, "control": 50, "lives": 3, "auto_align": 50})
            
            stat_rows = [
                {"label": "Speed",      "val": car_stats["speed"],      "max": 100, "color": (231, 76, 60),  "type": "bar"},
                {"label": "Control",    "val": car_stats["control"],    "max": 100, "color": (52, 152, 219), "type": "bar"},
                {"label": "Lives",      "val": car_stats["lives"],      "max": 5,   "color": (46, 204, 113), "type": "stars"},
            ]

            title_surf = title_font.render("VEHICLE REPOSITORY STATS", True, (255, 215, 0))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, 45)))

            pygame.draw.rect(self.game.screen, (44, 62, 80), left_panel, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), left_panel, 2, border_radius=12)
            
            car_img = self.game.assets.get_image(car_key)
            scaled_img = pygame.transform.scale(car_img, (int(car_img.get_width() * 1.4), int(car_img.get_height() * 1.4)))
            
            rotated_img = pygame.transform.rotate(scaled_img, spin_angle)
            rotated_rect = rotated_img.get_rect(center=(left_panel.centerx, left_panel.centery - 15))
            self.game.screen.blit(rotated_img, rotated_rect)
            
            name_surf = label_font.render(clean_name, True, (255, 255, 255))
            self.game.screen.blit(name_surf, name_surf.get_rect(center=(left_panel.centerx, left_panel.bottom - 25)))

            for idx, r_box in grid_rects:
                btn_car_key = self.game.car_options[idx]
                btn_name = btn_car_key.replace("_", " ").title()
                
                if idx == inspect_idx:
                    bg_col, text_col = (255, 215, 0), (0, 0, 0)
                elif r_box.collidepoint(mouse_pos):
                    bg_col, text_col = (52, 73, 94), (255, 255, 255)
                else:
                    bg_col, text_col = (44, 62, 80), (149, 165, 166)
                    
                pygame.draw.rect(self.game.screen, bg_col, r_box, border_radius=6)
                btn_txt = grid_font.render(btn_name, True, text_col)
                self.game.screen.blit(btn_txt, btn_txt.get_rect(center=r_box.center))

            for i, row in enumerate(stat_rows):
                curr_y = stats_y + (i * row_gap)
                
                lbl = label_font.render(row["label"], True, (255, 255, 255))
                self.game.screen.blit(lbl, (stats_x, curr_y))
                
                val_str = f"{row['val']}/{row['max']}" if row['type'] != "stars" else f"{row['val']} HP"
                val_surf = value_font.render(val_str, True, (200, 200, 200))
                self.game.screen.blit(val_surf, (stats_x + bar_max_w - val_surf.get_width(), curr_y + 4))
                
                if row["type"] == "bar":
                    track = pygame.Rect(stats_x, curr_y + 36, bar_max_w, bar_h)
                    pygame.draw.rect(self.game.screen, (30, 39, 46), track, border_radius=6)
                    
                    fill_w = int(bar_max_w * (row["val"] / row["max"]))
                    fill_rect = pygame.Rect(stats_x, curr_y + 36, fill_w, bar_h)
                    pygame.draw.rect(self.game.screen, row["color"], fill_rect, border_radius=6)
                    
                elif row["type"] == "stars":
                    star_img = self.game.assets.get_image('star')
                    
                    star_img = pygame.transform.scale(star_img, (45, 45))
                    
                    star_spacing = 40
                    for star_idx in range(row["val"]):
                        sx = stats_x + (star_idx * star_spacing)
                        sy = curr_y + 34
                        self.game.screen.blit(star_img, (sx, sy))

            align_y = stats_y + (3 * row_gap)
            
            align_lbl = label_font.render("Auto Align", True, (255, 255, 255))
            self.game.screen.blit(align_lbl, (stats_x, align_y))
            
            is_on = car_stats["auto_align"] > 50 
            status_text = "ON" if is_on else "OFF"
            status_color = (46, 204, 113) if is_on else (231, 76, 60)
            
            status_surf = title_font.render(status_text, True, status_color)
            self.game.screen.blit(status_surf, (stats_x, align_y + 32))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        viewing_stats = False
                    
                    for idx, r_box in grid_rects:
                        if r_box.collidepoint(event.pos):
                            inspect_idx = idx

            if back_btn.collidepoint(mouse_pos):
                b_color, b_border = (180, 180, 180), 0
            else:
                b_color, b_border = (100, 110, 120), 2
                
            pygame.draw.rect(self.game.screen, b_color, back_btn, b_border, border_radius=6)
            b_text = back_font.render("BACK", True, (255, 255, 255))
            self.game.screen.blit(b_text, b_text.get_rect(center=back_btn.center))
            
            pygame.display.flip()
            self.game.clock.tick(30)