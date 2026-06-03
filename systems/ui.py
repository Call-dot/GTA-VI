import pygame
import random
from settings import *

class Ui:
    def __init__(self, game):
        self.game = game

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
        exit_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        stats_btn_w, stats_btn_h = 160, 50
        stats_btn_rect = pygame.Rect(X_CENTRE - stats_btn_w / 2, HEIGHT - 20 - stats_btn_h, stats_btn_w, stats_btn_h)
        stats_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        car_name_font = pygame.font.SysFont("Arial", 18, bold=True)

        while selecting:
            self.game.screen.fill("#1B1B1B")
            
            welcome_font = pygame.font.SysFont("Arial", 70, bold=True) 
            welcome_surf = welcome_font.render("WELCOME TO GTA 6", True, (255, 215, 0)) 
            welcome_rect = welcome_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 0.8))
            self.game.screen.blit(welcome_surf, welcome_rect)
            
            title_surf = font.render("PICK YOUR RIDE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 1.5))
            self.game.screen.blit(title_surf, title_rect)

            footer_font = pygame.font.SysFont("Arial", 16, bold=False)
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
                            selecting = False
                    
                    if exit_btn_rect.collidepoint(click_pos):
                        pygame.quit()
                        import sys
                        sys.exit()
                        
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
            
            exit_text_surf = exit_font.render("EXIT GAME", True, (255, 255, 255))
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

    def stats_menu(self):
        viewing_stats = True
        title_font = pygame.font.SysFont("Arial", 45, bold=True)
        label_font = pygame.font.SysFont("Arial", 26, bold=True)
        value_font = pygame.font.SysFont("Arial", 22, bold=False)
        back_font = pygame.font.SysFont("Arial", 24, bold=True)
        grid_font = pygame.font.SysFont("Arial", 14, bold=True)
        
        # Track which car is being inspected (Default to the first one)
        inspect_idx = getattr(self, 'current_car_idx', 0)
        
        # Layout Buttons & Panels
        back_btn = pygame.Rect(20, HEIGHT - 70, 160, 50)
        left_panel = pygame.Rect(40, HEIGHT // 5, WIDTH // 2 - 60, HEIGHT // 2 - 20)
        
        # Generate an organized 3x3 selection grid under the left panel for all 9 cars
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
            
            car_stats = getattr(self, 'car_stats_database', {}).get(car_key, {"speed": 50, "control": 50, "lives": 3, "auto_align": 50})
            
            # --- REMOVED AUTO ALIGN FROM BARS LIST ---
            stat_rows = [
                {"label": "Speed",      "val": car_stats["speed"],      "max": 100, "color": (231, 76, 60)},
                {"label": "Control",    "val": car_stats["control"],    "max": 100, "color": (52, 152, 219)},
                {"label": "Lives",      "val": car_stats["lives"],      "max": 5,   "color": (46, 204, 113)},
            ]

            # 1. HEADER
            title_surf = title_font.render("VEHICLE REPOSITORY STATS", True, (255, 215, 0))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, 45)))

            # 2. LEFT DISPLAY PANEL
            pygame.draw.rect(self.game.screen, (44, 62, 80), left_panel, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), left_panel, 2, border_radius=12)
            
            car_img = self.game.assets.get_image(car_key)
            scaled_img = pygame.transform.scale(car_img, (int(car_img.get_width() * 1.4), int(car_img.get_height() * 1.4)))
            self.game.screen.blit(scaled_img, scaled_img.get_rect(center=(left_panel.centerx, left_panel.centery - 15)))
            
            name_surf = label_font.render(clean_name, True, (255, 255, 255))
            self.game.screen.blit(name_surf, name_surf.get_rect(center=(left_panel.centerx, left_panel.bottom - 25)))

            # 3. LOWER LEFT GRID
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

            # 4. RIGHT COLUMN: LABELS & STAT LINES (Speed, Control, Lives)
            for i, row in enumerate(stat_rows):
                curr_y = stats_y + (i * row_gap)
                
                lbl = label_font.render(row["label"], True, (255, 255, 255))
                self.game.screen.blit(lbl, (stats_x, curr_y))
                
                val_str = f"{row['val']}/{row['max']}" if row['label'] != "Lives" else f"{row['val']} HP"
                val_surf = value_font.render(val_str, True, (200, 200, 200))
                self.game.screen.blit(val_surf, (stats_x + bar_max_w - val_surf.get_width(), curr_y + 4))
                
                track = pygame.Rect(stats_x, curr_y + 36, bar_max_w, bar_h)
                pygame.draw.rect(self.game.screen, (30, 39, 46), track, border_radius=6)
                
                fill_w = int(bar_max_w * (row["val"] / row["max"]))
                fill_rect = pygame.Rect(stats_x, curr_y + 36, fill_w, bar_h)
                pygame.draw.rect(self.game.screen, row["color"], fill_rect, border_radius=6)

            # 5. SPECIAL RENDER: AUTO ALIGN AS ON/OFF TEXT ONLY
            # Positioned cleanly directly beneath the 3 standard stat rows
            align_y = stats_y + (3 * row_gap)
            
            align_lbl = label_font.render("Auto Align", True, (255, 255, 255))
            self.game.screen.blit(align_lbl, (stats_x, align_y))
            
            # Read from database: if value > 50 consider it ON, otherwise OFF
            # (Or modify your database map directly to use True/False if preferred!)
            is_on = car_stats["auto_align"] > 50 
            status_text = "ON" if is_on else "OFF"
            status_color = (46, 204, 113) if is_on else (231, 76, 60) # Green if ON, Red if OFF
            
            status_surf = title_font.render(status_text, True, status_color)
            self.game.screen.blit(status_surf, (stats_x, align_y + 32))

            # 6. INPUT EVENT MONITORING
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