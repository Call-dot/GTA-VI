import pygame
import random
import math
import sys
from systems.asset_loader import AssetLoader
from settings import *
from entities.npc import Npc
from saves import (
    save_run, load_all_saves, export_save, import_save,
    format_gametime, delete_save,
)

class Ui:
    def __init__(self, game):
        self.game = game
        self.assets = game.assets
        self.fonts = {
            "title": self.assets.get_font("ops"),
            "subtitle": self.assets.get_font("pixelify"),
            "header": self.assets.get_font("ops"),
            "body": self.assets.get_font("bungee"),
            "bungeeshade": self.assets.get_font("bungeeshade"),
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
                    sys.exit()
            self.game.screen.fill("#1B1B1B")
            logo = self.assets.get_image("strockstar")
            logo_rect = logo.get_rect(center=(X_CENTRE, Y_CENTRE))
            self.game.screen.blit(logo, logo_rect)
            pygame.display.flip()
            dt = self.game.clock.tick(30) / 1000
            t += dt

    def main_menu(self):
        """Displays the Main Menu with New Game, Load Game, Saves, Settings, and Exit."""
        menu_running = True
        self.game.music[1] = False
        self.game.vlc("title", -1, False)

        while menu_running:
            WIDTH  = self.game.screen.get_width()
            HEIGHT = self.game.screen.get_height()
            X_CENTRE, Y_CENTRE = WIDTH // 2, HEIGHT // 2

            btn_w, btn_h = 240, 55
            new_game_btn  = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE - 105, btn_w, btn_h)
            load_game_btn = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE - 40,  btn_w, btn_h)
            saves_btn     = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE + 25,  btn_w, btn_h)
            settings_btn  = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE + 90,  btn_w, btn_h)

            exit_btn_w, exit_btn_h = 220, 50
            exit_game_btn = pygame.Rect(20, HEIGHT - 20 - exit_btn_h, exit_btn_w, exit_btn_h)

            def draw_main_menu_content():
                self.game.screen.fill("#1B1B1B")

                title_surf = self.fonts["title"].render("GRAND THEFT AUTO VI", True, (255, 215, 0))
                title_rect = title_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 175))
                self.game.screen.blit(title_surf, title_rect)

                mouse_pos = pygame.mouse.get_pos()

                new_color      = (0, 200, 100)   if new_game_btn.collidepoint(mouse_pos)  else (44, 62, 80)
                load_color     = (52, 152, 219)  if load_game_btn.collidepoint(mouse_pos) else (44, 62, 80)
                saves_color    = (230, 126, 34)  if saves_btn.collidepoint(mouse_pos)     else (44, 62, 80)
                settings_color = (155, 89, 182)  if settings_btn.collidepoint(mouse_pos)  else (44, 62, 80)
                exit_color     = (130, 20, 20)   if exit_game_btn.collidepoint(mouse_pos) else (200, 50, 50)

                pygame.draw.rect(self.game.screen, new_color,      new_game_btn,  border_radius=8)
                pygame.draw.rect(self.game.screen, load_color,     load_game_btn, border_radius=8)
                pygame.draw.rect(self.game.screen, saves_color,    saves_btn,     border_radius=8)
                pygame.draw.rect(self.game.screen, settings_color, settings_btn,  border_radius=8)
                pygame.draw.rect(self.game.screen, exit_color,     exit_game_btn, border_radius=6)

                new_text = self.fonts["body"].render("NEW GAME", True, (255, 255, 255))
                self.game.screen.blit(new_text, new_text.get_rect(center=new_game_btn.center))

                load_text = self.fonts["body"].render("LOAD GAME", True, (255, 255, 255))
                self.game.screen.blit(load_text, load_text.get_rect(center=load_game_btn.center))

                saves_text = self.fonts["body"].render("SAVES", True, (255, 255, 255))
                self.game.screen.blit(saves_text, saves_text.get_rect(center=saves_btn.center))

                settings_text = self.fonts["body"].render("SETTINGS", True, (255, 255, 255))
                self.game.screen.blit(settings_text, settings_text.get_rect(center=settings_btn.center))

                exit_text = self.fonts["body"].render("EXIT GAME", True, (255, 255, 255))
                self.game.screen.blit(exit_text, exit_text.get_rect(center=exit_game_btn.center))

            draw_main_menu_content()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if new_game_btn.collidepoint(event.pos):
                            self.game.is_loaded_save = False
                            menu_running = False
                            return True

                        elif load_game_btn.collidepoint(event.pos):
                            self.game.is_loaded_save = True
                            menu_running = False
                            return True

                        elif saves_btn.collidepoint(event.pos):
                            self.saves_menu()

                        elif settings_btn.collidepoint(event.pos):
                            self.settings_menu()

                        elif exit_game_btn.collidepoint(event.pos):
                            self.confirm_exit_popup(draw_background_callback=draw_main_menu_content)

            pygame.display.flip()
            self.game.clock.tick(30)
    
    def pause_menu(self):
        """Displays an extra large popup overlay over the current game state when paused."""
        paused = True
        
        WIDTH  = self.game.screen.get_width()
        HEIGHT = self.game.screen.get_height()
        X_CENTRE, Y_CENTRE = WIDTH // 2, HEIGHT // 2

        # --- INCREASED: Expanded height to 380 to fit three buttons comfortably ---
        box_w, box_h = 540, 380
        popup_rect = pygame.Rect(X_CENTRE - box_w // 2, Y_CENTRE - box_h // 2, box_w, box_h)

        # --- RE-ALIGNED: Clean 3-button stack positioning ---
        btn_w, btn_h = 380, 55
        continue_btn = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE - 40, btn_w, btn_h)
        exit_btn     = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE + 25, btn_w, btn_h)
        quit_btn     = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE + 90, btn_w, btn_h)

        while paused:
            mouse_pos = pygame.mouse.get_pos()
            
            pygame.draw.rect(self.game.screen, (30, 43, 56), popup_rect, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), popup_rect, 2, border_radius=12) # Gold border

            title_surf = self.fonts["header"].render("GAME PAUSED", True, (255, 255, 255))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 120)))

            continue_color = (0, 200, 100) if continue_btn.collidepoint(mouse_pos) else (44, 62, 80)
            exit_color     = (200, 50, 50)  if exit_btn.collidepoint(mouse_pos)     else (44, 62, 80)
            quit_color     = (150, 25, 25)  if quit_btn.collidepoint(mouse_pos)     else (44, 62, 80)

            pygame.draw.rect(self.game.screen, continue_color, continue_btn, border_radius=6)
            pygame.draw.rect(self.game.screen, exit_color, exit_btn, border_radius=6)
            pygame.draw.rect(self.game.screen, quit_color, quit_btn, border_radius=6)

            cont_txt = self.fonts["body"].render("CONTINUE", True, (255, 255, 255))
            self.game.screen.blit(cont_txt, cont_txt.get_rect(center=continue_btn.center))

            exit_txt = self.fonts["body"].render("EXIT TO MENU", True, (255, 255, 255))
            self.game.screen.blit(exit_txt, exit_txt.get_rect(center=exit_btn.center))

            quit_txt = self.fonts["body"].render("QUIT GAME", True, (255, 255, 255))
            self.game.screen.blit(quit_txt, quit_txt.get_rect(center=quit_btn.center))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if continue_btn.collidepoint(event.pos):
                            paused = False 
                            
                        elif exit_btn.collidepoint(event.pos):
                            paused = False
                            return "exit" 
                        
                        elif quit_btn.collidepoint(event.pos):
                            pygame.quit()
                            import sys
                            sys.exit()

            pygame.display.flip()
            self.game.clock.tick(30)
            
        return "continue"

    # Written by me, polished by AI to look nicer and run cleaner
    def saves_menu(self):
        """
        Full-screen saves browser.

        LEFT COLUMN  - Import / Export buttons + feedback label
        RIGHT COLUMN - Scrollable list of saved runs (click to replay)
        BOTTOM-LEFT  - Back button
        """
        PAD           = 24
        LEFT_W        = 260          
        RIGHT_X       = PAD + LEFT_W + PAD 
        RIGHT_W       = WIDTH - RIGHT_X - PAD
        LIST_Y        = 80 
        LIST_H        = HEIGHT - LIST_Y - PAD
        CARD_H        = 90
        CARD_GAP      = 8
        CARD_STRIDE   = CARD_H + CARD_GAP

        BG            = (27, 27, 27)
        PANEL_BG      = (34, 47, 62)
        ACCENT        = (255, 215, 0)
        BTN_IDLE      = (44, 62, 80)
        BTN_HOV_IMP   = (39, 174, 96)
        BTN_HOV_EXP   = (41, 128, 185)
        BTN_BACK      = (100, 110, 120)
        BTN_BACK_HOV  = (140, 150, 160)
        REPLAY_HOV    = (52, 73, 94)
        TEXT_DIM      = (149, 165, 166)
        PASS_COL      = (46, 204, 113)
        FAIL_COL      = (231, 76, 60)

        f_label  = pygame.font.SysFont("Arial", 22, bold=True)
        f_body   = pygame.font.SysFont("Arial", 18)
        f_small  = pygame.font.SysFont("Arial", 14)
        f_title  = pygame.font.SysFont("Arial", 32, bold=True)

        btn_w, btn_h = LEFT_W, 52
        import_btn = pygame.Rect(PAD, 100, btn_w, btn_h)
        export_btn = pygame.Rect(PAD, 170, btn_w, btn_h)
        back_btn   = pygame.Rect(PAD, HEIGHT - PAD - btn_h, btn_w, btn_h)

        list_clip  = pygame.Rect(RIGHT_X, LIST_Y, RIGHT_W, LIST_H)

        records          = load_all_saves()
        scroll_y         = 0        # pixels scrolled down
        drag_start_y     = None     # y coord where mouse-drag began
        drag_start_scroll= 0
        feedback_msg     = ""       # shown under the buttons
        feedback_timer   = 0.0
        selected_idx     = None     # index of the highlighted run card

        star_raw = self.game.assets.get_image("star")
        star_img = pygame.transform.smoothscale(star_raw, (22, 22))

        def total_list_h():
            return max(len(records) * CARD_STRIDE, 1)

        def max_scroll():
            return max(0, total_list_h() - LIST_H)

        def set_feedback(msg: str, duration: float = 2.5):
            nonlocal feedback_msg, feedback_timer
            feedback_msg   = msg
            feedback_timer = duration

        def card_rect_for(idx: int) -> pygame.Rect:
            """Screen rect of card *idx* accounting for scroll."""
            return pygame.Rect(
                RIGHT_X,
                LIST_Y + idx * CARD_STRIDE - scroll_y,
                RIGHT_W,
                CARD_H,
            )

        def draw_card(rec: dict, idx: int, hovered: bool):
            r   = card_rect_for(idx)
            # skip if fully outside the visible list band
            if r.bottom < LIST_Y or r.top > LIST_Y + LIST_H:
                return
            # clip top/bottom to list window for the draw call
            draw_r = r.clip(list_clip)
            if draw_r.height == 0:
                return

            bg_col = REPLAY_HOV if hovered else PANEL_BG
            pygame.draw.rect(self.game.screen, bg_col, r, border_radius=8)
            if hovered:
                pygame.draw.rect(self.game.screen, ACCENT, r, 2, border_radius=8)

            car_key = rec.get("car_model", "")
            try:
                car_img = self.game.assets.get_image(car_key)
                thumb   = pygame.transform.smoothscale(car_img, (54, 54))
                self.game.screen.blit(thumb, (r.x + 8, r.centery - 27))
            except Exception:
                pass   # no image – leave blank

            tx = r.x + 72

            # seed
            seed_s = f_label.render(f"Seed {rec.get('seed', '?')}", True, (255, 255, 255))
            self.game.screen.blit(seed_s, (tx, r.y + 8))

            # time
            time_str = format_gametime(rec.get("igt", 0), DEPARTURE_TIME)
            time_s   = f_body.render(time_str, True, TEXT_DIM)
            self.game.screen.blit(time_s, (tx, r.y + 34))

            # pass/fail badge
            passed   = rec.get("success", False)
            badge_col= PASS_COL if passed else FAIL_COL
            badge_txt= "PASSED" if passed else "FAILED"
            badge_s  = f_small.render(badge_txt, True, badge_col)
            self.game.screen.blit(badge_s, (tx, r.y + 58))

            health   = rec.get("health", 0)
            star_gap = 26
            stars_total_w = health * star_gap
            sx = r.right - stars_total_w - 10
            sy = r.centery - star_img.get_height() // 2
            for _ in range(health):
                self.game.screen.blit(star_img, (sx, sy))
                sx += star_gap

            if hovered:
                hint_s = f_small.render("Click to replay", True, ACCENT)
                self.game.screen.blit(hint_s, (r.right - hint_s.get_width() - 8, r.bottom - 20))

        def draw():
            self.game.screen.fill(BG)

            # header
            hdr = f_title.render("SAVES", True, ACCENT)
            self.game.screen.blit(hdr, hdr.get_rect(midtop=(X_CENTRE, 20)))

            mouse  = pygame.mouse.get_pos()

            # divider line
            pygame.draw.line(self.game.screen, (60, 70, 80),
                             (RIGHT_X - PAD // 2, 80),
                             (RIGHT_X - PAD // 2, HEIGHT - 80), 1)

            for btn, label, hov_col in [
                (import_btn, "IMPORT SAVE", BTN_HOV_IMP),
                (export_btn, "EXPORT SAVE", BTN_HOV_EXP),
            ]:
                col = hov_col if btn.collidepoint(mouse) else BTN_IDLE
                pygame.draw.rect(self.game.screen, col, btn, border_radius=7)
                txt = f_label.render(label, True, (255, 255, 255))
                self.game.screen.blit(txt, txt.get_rect(center=btn.center))

            # feedback label
            if feedback_msg:
                fb_s = f_small.render(feedback_msg, True, ACCENT)
                self.game.screen.blit(fb_s, (PAD, export_btn.bottom + 12))

            # back button
            b_col = BTN_BACK_HOV if back_btn.collidepoint(mouse) else BTN_BACK
            pygame.draw.rect(self.game.screen, b_col, back_btn, border_radius=7)
            b_txt = f_label.render("< BACK", True, (255, 255, 255))
            self.game.screen.blit(b_txt, b_txt.get_rect(center=back_btn.center))

            col_hdr = f_label.render(
                f"{len(records)} run{'s' if len(records) != 1 else ''}  ·  sorted by stars → time → seed",
                True, TEXT_DIM)
            self.game.screen.blit(col_hdr, (RIGHT_X, 50))

            prev_clip = self.game.screen.get_clip()
            self.game.screen.set_clip(list_clip)

            hovered_card = None
            if list_clip.collidepoint(mouse):
                raw_idx = (mouse[1] - LIST_Y + scroll_y) // CARD_STRIDE
                if 0 <= raw_idx < len(records):
                    hovered_card = raw_idx

            for i, rec in enumerate(records):
                draw_card(rec, i, i == hovered_card)

            if not records:
                empty_s = f_body.render("No saved runs yet.", True, TEXT_DIM)
                self.game.screen.blit(empty_s, empty_s.get_rect(center=list_clip.center))

            self.game.screen.set_clip(prev_clip)

            if total_list_h() > LIST_H:
                bar_x     = RIGHT_X + RIGHT_W + 4
                bar_h_tot = LIST_H
                thumb_h   = max(30, int(bar_h_tot * LIST_H / total_list_h()))
                thumb_y   = LIST_Y + int((scroll_y / max_scroll()) * (bar_h_tot - thumb_h))
                pygame.draw.rect(self.game.screen, (60, 70, 80),
                                 pygame.Rect(bar_x, LIST_Y, 6, bar_h_tot), border_radius=3)
                pygame.draw.rect(self.game.screen, ACCENT,
                                 pygame.Rect(bar_x, thumb_y, 6, thumb_h), border_radius=3)

            pygame.display.flip()
            return hovered_card   # so the event handler knows what's under the cursor

        running = True
        clock   = self.game.clock
        while running:
            dt           = clock.tick(30) / 1000
            feedback_timer = max(0.0, feedback_timer - dt)
            if feedback_timer == 0.0:
                feedback_msg = ""

            hovered_card = draw()
            mouse        = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEWHEEL:
                    scroll_y = max(0, min(scroll_y - event.y * 30, max_scroll()))

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos

                    # back
                    if back_btn.collidepoint(pos):
                        running = False

                    # import
                    elif import_btn.collidepoint(pos):
                        rec = import_save()
                        if rec:
                            records = load_all_saves()  # reload sorted
                            set_feedback("Save imported successfully.")
                        else:
                            set_feedback("Import cancelled or file invalid.")

                    # export
                    elif export_btn.collidepoint(pos):
                        if selected_idx is not None and 0 <= selected_idx < len(records):
                            ok = export_save(records[selected_idx]["_path"])
                            set_feedback("Exported!" if ok else "Export cancelled.")
                        elif hovered_card is not None:
                            ok = export_save(records[hovered_card]["_path"])
                            set_feedback("Exported!" if ok else "Export cancelled.")
                        else:
                            set_feedback("Hover over or click a run first.")

                    # click on a run card → replay
                    elif list_clip.collidepoint(pos) and hovered_card is not None:
                        self._launch_replay(records[hovered_card])
                        # After replay returns we come back to this screen
                        records = load_all_saves()

                    # start drag (for click-and-drag scrolling)
                    elif list_clip.collidepoint(pos):
                        drag_start_y      = pos[1]
                        drag_start_scroll = scroll_y

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    drag_start_y = None

                if event.type == pygame.MOUSEMOTION:
                    if drag_start_y is not None:
                        delta    = drag_start_y - event.pos[1]
                        scroll_y = max(0, min(drag_start_scroll + delta, max_scroll()))

    # Written by AI
    # Just thought it would be a cool feature since I 
    # already made the capabilities for implementing this when designing original game structure
    def _launch_replay(self, record: dict):
        """
        Restore game state from *record* and run a full replay.
        The game loop in main.py's run() is NOT reused; we trigger it
        by setting the necessary game fields and calling gaming = True,
        then returning control to the caller (saves_menu) once gaming = False.
        """
        g = self.game

        # ── reset base state (mirrors new_game) ───────────────────────
        g.playeropacity   = 255
        g.health          = record.get("health", 5)
        g.playerspeed     = 0
        g.playerpos       = 0
        g.chased          = False
        g.igt             = record.get("igt", 0)  # start clock at final time
        g.success         = False
        g.respect         = False

        g.player_x        = X_CENTRE
        g.player_y        = HEIGHT - SPACE_ABOVE_PLAYER
        g.player_vx       = 0
        g.player_rect     = None
        g.player_hitbox   = None
        g.playerangle     = 0
        g.tutorial        = False      # skip tutorial in replays
        g.tiler.almost_there = False

        g.npcs.empty()
        g.enemies.empty()
        g.all_sprites.empty()

        # ── restore map data from the save ────────────────────────────
        g.tiles     = list(record.get("tiles",     []))
        g.tile_data = list(record.get("tile_data", []))
        g.endpoint  = record.get("endpoint", None)

        # weathering must parallel tiles length
        g.weathering = [g.bg_generator("weathering") for _ in g.tiles]
        g.scroll_offset = 0
        g.x_offset      = 0
        g.ts_down       = 0

        # ── restore car ───────────────────────────────────────────────
        car_key = record.get("car_model", "")
        if car_key and car_key in g.car_options:
            g.player_model = car_key
            g.player_img   = g.assets.get_image(car_key)
        else:
            # fall back to first available car
            g.player_model = g.car_options[0]
            g.player_img   = g.assets.get_image(g.car_options[0])

        # ── run the game loop (same as Game.run's inner while) ────────
        g.gaming = True
        g.vlc("theme", -1, False)

        while g.gaming:
            g.vlc("theme", -1, False)
            g.dt = g.clock.tick(30) / 1000
            g.t  += g.dt
            g.events()
            g.playerinput(g.dt)
            g.player()
            g.update()
            g.bg_tiler()
            g.draw()

        # ── show end screen ───────────────────────────────────────────
        g.end_run()


    def settings_menu(self):
        """Displays a simple settings menu featuring the interactive volume slider and fullscreen toggle."""
        in_settings = True

        while in_settings:
            # Re-fetch every loop iteration so elements rearrange instantly when window mode alters
            WIDTH  = self.game.screen.get_width()
            HEIGHT = self.game.screen.get_height()
            X_CENTRE, Y_CENTRE = WIDTH // 2, HEIGHT // 2

            slider_w, slider_h = 300, 12
            volume_slider = VolumeSlider(
                x=X_CENTRE - slider_w // 2,
                y=Y_CENTRE - 20,  
                width=slider_w,
                height=slider_h,
                initial_val=pygame.mixer.music.get_volume()
            )

            fullscreen_btn = pygame.Rect(X_CENTRE - 120, Y_CENTRE + 50, 240, 50)
            
            back_btn_w, back_btn_h = 160, 50
            back_btn = pygame.Rect(20, HEIGHT - 20 - back_btn_h, back_btn_w, back_btn_h)

            mouse_pos = pygame.mouse.get_pos()
            self.game.screen.fill("#1B1B1B")

            title_surf = self.fonts["header"].render("SETTINGS", True, (255, 255, 255))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 120)))

            vol_pct  = int(volume_slider.value * 100)
            vol_surf = self.fonts["body"].render(f"MUSIC VOLUME: {vol_pct}%", True, (255, 255, 255))
            self.game.screen.blit(vol_surf, vol_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 50)))
            
            volume_slider.draw(self.game.screen)

            is_fs = getattr(self.game, 'is_fullscreen', False)
            fs_text_str = "WINDOW MODE" if is_fs else "FULLSCREEN"
            
            fs_bg_color = (44, 62, 80) if fullscreen_btn.collidepoint(mouse_pos) else (30, 43, 56)
            pygame.draw.rect(self.game.screen, fs_bg_color, fullscreen_btn, border_radius=6)
            
            fs_text_surf = self.fonts["body"].render(fs_text_str, True, (255, 255, 255))
            self.game.screen.blit(fs_text_surf, fs_text_surf.get_rect(center=fullscreen_btn.center))

            back_bg_color = (44, 62, 80) if back_btn.collidepoint(mouse_pos) else (30, 43, 56)
            pygame.draw.rect(self.game.screen, back_bg_color, back_btn, border_radius=6)
            
            back_text = self.fonts["body"].render("< BACK", True, (255, 255, 255))
            self.game.screen.blit(back_text, back_text.get_rect(center=back_btn.center))

            # 5. Input System Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                if volume_slider.handle_event(event):
                    pygame.mixer.music.set_volume(volume_slider.value)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Fullscreen Logic Block
                        if fullscreen_btn.collidepoint(event.pos):
                            if is_fs:
                                # Return to default window configurations. 
                                # Tip: Replace 1280, 720 with your game's original base window sizes if different.
                                base_w, base_h = 1280, 720 
                                self.game.screen = pygame.display.set_mode((base_w, base_h))
                                self.game.is_fullscreen = False
                            else:
                                # Fetch native display monitor dimensions to eliminate off-center drift
                                display_info = pygame.display.Info()
                                native_w = display_info.current_w
                                native_h = display_info.current_h
                                
                                self.game.screen = pygame.display.set_mode(
                                    (native_w, native_h), 
                                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                                )
                                self.game.is_fullscreen = True

                        # Back Action
                        if back_btn.collidepoint(event.pos):
                            in_settings = False

            pygame.display.flip()
            self.game.clock.tick(30)

    def intro_screen(self):
        t = 0
        pygame.mixer.music.stop()
        while t < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
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
        finale = True if self.game.success else False
        self.game.playerpos = 0
        self.game.playerspeed = 0
        self.game.scroll_offset = 0
        player_img = self.game.player_img
        player_rect = player_img.get_rect()
        player_turn = 0
        queue = int(finaletime * QUEUE_INTENSITY)
        npcs = []
        pygame.mixer.music.stop()
        self.game.music[1] = False
        self.game.vlc("shepard", -1, False)

        tiles = ["4C5-,:,-6C3", "SC+:+:+:+CS", "SC+:+:+:+CS", "__SC,:,:,:,CS_@"]
        tiles.extend(["SC+:+:+:+CS" if i % 2 else "SC$:+:+:$CS" for i in range(queue)])
        tiles.extend(["______SC+:+:+:+-2999999", "______SC+`+`+`+`+`+`+`+", "______SC+`+`+`+`+`+`+`+", "______SC+`+`+`+`+`+`+`+", "______SC+:+:+:+-4000000"])
        tiles.extend(["SC+:+:+:+CS" for _ in range(25)])

        for row_idx, row in enumerate(tiles):
            for col_idx, char in enumerate(row):
                if char != "$":
                    continue

                _, image = self.assets.get_random_car(self.game.player_model)
                road_width = (len(row) - 1) * ROAD_SIZE_X
                x_start = X_CENTRE - road_width / 2

                npcs.append({
                    "image": image,
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

            intersection_screen_y = (intersection_row * TILE_SIZE_Y - self.game.playerpos * TILE_SIZE_Y + self.game.scroll_offset)
            intersection_rect = pygame.Rect(0, intersection_screen_y + TILE_SIZE_Y, WIDTH, TILE_SIZE_Y)

            if t < 2:
                player_y = t * TILE_SIZE_Y
                player_x = ROAD_SIZE_X * 2 * math.sin(player_y * math.pi / (4 * TILE_SIZE_Y)) + X_CENTRE + ROAD_SIZE_X
                playerangle = math.sin(player_y * math.pi * 2 / (4 * TILE_SIZE_Y)) * 30
                player_rotated = pygame.transform.rotate(player_img, playerangle + 180)
                rect = player_rotated.get_rect(center=(player_x, player_y))
                self.game.screen.blit(player_rotated, rect)
            elif player_rect.colliderect(intersection_rect):
                player_turn += dt * 1.5
                if player_turn > 1:
                    player_turn = 1
                p = player_turn
                player_x += 2 ** (p * 10)
                player_y += TILE_SIZE_Y * 0.25 * (1 - math.cos(p * math.pi / 2))
                playerangle = 180 + 90 * p
                player_rotated = pygame.transform.rotate(player_img, playerangle)
                rect = player_rotated.get_rect(center=(player_x, player_y))
                self.game.screen.blit(player_rotated, rect)
            else:
                player_y = 2 * TILE_SIZE_Y
                player_x = X_CENTRE + 3 * ROAD_SIZE_X
                player_rotated = pygame.transform.rotate(player_img, 180)
                player_rect = player_img.get_rect(center=(player_x, player_y))
                self.game.screen.blit(player_rotated, player_rect)

            for npc in npcs:
                screen_y = npc["world_y"]
                screen_x = npc["world_x"]

                if not npc["turning"]:
                    npc_rect = npc["image"].get_rect(center=(screen_x, screen_y))
                    if npc_rect.colliderect(intersection_rect):
                        npc["turning"] = True
                else:
                    npc["turn_progress"] += dt * 1.5
                    if npc["turn_progress"] > 1:
                        npc["turn_progress"] = 1
                    p = npc["turn_progress"]
                    npc["angle"] = 180 + 90 * p

            for npc in npcs:
                screen_y = npc["world_y"]
                screen_x = npc["world_x"]
                draw_x = screen_x
                draw_y = screen_y

                if npc["turning"]:
                    p = npc["turn_progress"]
                    draw_x += 2 ** (p * 10)
                    draw_y += TILE_SIZE_Y * 0.25 * (1 - math.cos(p * math.pi / 2))

                rotated = pygame.transform.rotate(npc["image"], npc["angle"])
                rect = rotated.get_rect(center=(draw_x, draw_y))
                self.game.screen.blit(rotated, rect)

            clock_surf = self.fonts["highlight"].render(self.game.gametime(), True, ("#FEFEFE"))
            clock_rect = clock_surf.get_rect(center=(X_CENTRE, Y_CENTRE))

            if player_x > WIDTH:
                finale = False
                return True if self.game.igt + DEPARTURE_TIME <= DEADLINE else False
            else:
                self.game.screen.blit(clock_surf, clock_rect)

            pygame.display.flip()

    def confirm_exit_popup(self, draw_background_callback=None):
        confirming = True
        popup_w, popup_h = 400, 200
        popup_rect = pygame.Rect(X_CENTRE - popup_w // 2, Y_CENTRE - popup_h // 2, popup_w, popup_h)

        btn_w, btn_h = 120, 45
        yes_btn = pygame.Rect(popup_rect.centerx - btn_w - 20, popup_rect.bottom - btn_h - 30, btn_w, btn_h)
        no_btn  = pygame.Rect(popup_rect.centerx + 20,         popup_rect.bottom - btn_h - 30, btn_w, btn_h)

        while confirming:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    if no_btn.collidepoint(event.pos):
                        return False

            if draw_background_callback:
                draw_background_callback()
            else:
                self.game.screen.fill("#1B1B1B")

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.game.screen.blit(overlay, (0, 0))

            pygame.draw.rect(self.game.screen, (34, 47, 62), popup_rect, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), popup_rect, 3, border_radius=12)

            msg_surf = self.fonts["highlight"].render("ARE YOU SURE?", True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(popup_rect.centerx, popup_rect.top + 45))
            self.game.screen.blit(msg_surf, msg_rect)

            yes_color = (200, 50, 50)  if yes_btn.collidepoint(mouse_pos) else (140, 30, 30)
            no_color  = (100, 110, 120) if no_btn.collidepoint(mouse_pos) else (60, 70, 80)

            pygame.draw.rect(self.game.screen, yes_color, yes_btn, border_radius=6)
            pygame.draw.rect(self.game.screen, no_color,  no_btn,  border_radius=6)

            yes_surf = self.fonts["body"].render("YES", True, (255, 255, 255))
            no_surf  = self.fonts["body"].render("NO",  True, (255, 255, 255))

            self.game.screen.blit(yes_surf, yes_surf.get_rect(center=yes_btn.center))
            self.game.screen.blit(no_surf,  no_surf.get_rect(center=no_btn.center))

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

        self.game.music[1] = False
        self.game.vlc("menu", -1, False)

        rects = []
        for idx in range(len(self.game.car_options)):
            if idx < 5:
                x = row1_start_x + idx * (card_w + spacing_x)
                y = row1_y
            else:
                x = row2_start_x + (idx - 5) * (card_w + spacing_x)
                y = row2_y
            rects.append(pygame.Rect(x, y, card_w, card_h))

        exit_btn_w, exit_btn_h = 220, 50
        exit_btn_rect = pygame.Rect(20, HEIGHT - 20 - exit_btn_h, exit_btn_w, exit_btn_h)

        back_btn_w, back_btn_h = 160, 50
        back_btn_rect = pygame.Rect(20, 20, back_btn_w, back_btn_h)

        stats_btn_w, stats_btn_h = 160, 50
        stats_btn_rect = pygame.Rect(X_CENTRE - stats_btn_w / 2, HEIGHT - 20 - stats_btn_h, stats_btn_w, stats_btn_h)
        
        stats_font    = self.fonts["body"] 
        car_name_font = self.fonts["caption"] 

        def draw_everything():
            self.game.screen.fill("#1B1B1B")

            welcome_surf = self.fonts["highlight"].render("WELCOME TO GTA 6", True, (255, 215, 0))
            welcome_rect = welcome_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 0.8))
            self.game.screen.blit(welcome_surf, welcome_rect)

            title_surf = self.fonts["header"].render("PICK YOUR RIDE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 1.5))
            self.game.screen.blit(title_surf, title_rect)

            footer_surf1 = self.fonts["caption"].render("v1.0.0 Alpha", True, (120, 120, 125))
            footer_rect1 = footer_surf1.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))
            footer_surf2 = self.fonts["caption"].render("Developed by Aiden, Tristan, and Carey", True, (120, 120, 125))
            footer_rect2 = footer_surf2.get_rect(bottomright=footer_rect1.topright)
            self.game.screen.blit(footer_surf1, footer_rect1)
            self.game.screen.blit(footer_surf2, footer_rect2)

            curr_mouse = pygame.mouse.get_pos()

            for idx, rect in enumerate(rects):
                if rect.collidepoint(curr_mouse):
                    color, border = (0, 200, 100), 5
                else:
                    color, border = (180, 180, 180), 2

                pygame.draw.rect(self.game.screen, color, rect, border, border_radius=12)
                car_surface = self.game.assets.get_image(self.game.car_options[idx])
                car_rect    = car_surface.get_rect(center=(rect.centerx, rect.centery - 15))
                self.game.screen.blit(car_surface, car_rect)

                clean_name = self.game.car_options[idx].replace("_", " ").title()
                name_surf  = car_name_font.render(clean_name, True, (255, 255, 255))
                name_rect  = name_surf.get_rect(center=(rect.centerx, rect.bottom - 20))
                self.game.screen.blit(name_surf, name_rect)

            exit_bg_color    = (130, 20, 20) if exit_btn_rect.collidepoint(curr_mouse) else (200, 50, 50)
            exit_border_width = 0 if exit_btn_rect.collidepoint(curr_mouse) else 2
            pygame.draw.rect(self.game.screen, exit_bg_color, exit_btn_rect, exit_border_width, border_radius=6)

            exit_text_surf = self.fonts["body"].render("EXIT GAME", True, (255, 255, 255))
            self.game.screen.blit(exit_text_surf, exit_text_surf.get_rect(center=exit_btn_rect.center))

            stats_bg_color    = (20, 100, 130) if stats_btn_rect.collidepoint(curr_mouse) else (50, 150, 200)
            stats_border_width = 0 if stats_btn_rect.collidepoint(curr_mouse) else 2
            pygame.draw.rect(self.game.screen, stats_bg_color, stats_btn_rect, stats_border_width, border_radius=6)

            stats_text_surf = stats_font.render("STATS", True, (255, 255, 255))
            self.game.screen.blit(stats_text_surf, stats_text_surf.get_rect(center=stats_btn_rect.center))

            back_bg_color    = (130, 20, 20) if back_btn_rect.collidepoint(curr_mouse) else (200, 50, 50)
            back_border_width = 0 if back_btn_rect.collidepoint(curr_mouse) else 2
            pygame.draw.rect(self.game.screen, back_bg_color, back_btn_rect, back_border_width, border_radius=6)

            back_text_surf = self.fonts["body"].render("< BACK", True, (255, 255, 255))
            self.game.screen.blit(back_text_surf, back_text_surf.get_rect(center=back_btn_rect.center))

        while selecting:
            draw_everything()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    click_pos = event.pos
                    for idx, rect in enumerate(rects):
                        if rect.collidepoint(click_pos):
                            chosen_key = self.game.car_options[idx]
                            self.game.player_model = chosen_key
                            self.game.player_img   = self.game.assets.get_image(chosen_key)
                            self.game.current_car_idx = idx
                            self.game.playerdata = self.game.stat_presets[chosen_key]
                            self.game.max_speed = MAX_SPEED * (self.game.playerdata["speed"] / 100 + 0.5)
                            self.game.handling = HANDLING * self.game.playerdata["control"] / 100
                            self.game.health = self.game.playerdata["lives"]
                            self.game.autoalign = self.game.playerdata["auto_align"]
                            selecting = False
                            return True

                    if exit_btn_rect.collidepoint(click_pos):
                        self.confirm_exit_popup(draw_background_callback=draw_everything)

                    if back_btn_rect.collidepoint(click_pos):
                        return False

                    if stats_btn_rect.collidepoint(click_pos):
                        hovered_idx = 0
                        for idx, rect in enumerate(rects):
                            if rect.collidepoint(pygame.mouse.get_pos()):
                                hovered_idx = idx
                        self.game.current_car_idx = hovered_idx
                        self.stats_menu()

            pygame.display.flip()
            self.game.clock.tick(30)

    def ending(self, respect):
        result = respect
        t = 0
        overlay = pygame.Surface((WIDTH, 420), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.game.screen.blit(overlay, (0, 180))
        while t < 3:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if result:
                mission_surf1 = self.fonts["bungeeshade"].render("MiSSiON PaSSeD", True, ("#FEFEFE"))
                mission_surf2 = self.fonts["caption"].render("Get to school", True, ("#FEFEFE"))
                star_surf     = self.fonts["body"].render(("ReSPeCT: " if self.game.health else "ReSPeCT: NONE"), True, ("#FEFEFE"))
            else:
                mission_surf1 = self.fonts["bungeeshade"].render("MiSSiON FaiLeD", True, ("#FEFEFE"))
                mission_surf2 = self.fonts["caption"].render("You're late!", True, ("#FEFEFE"))
            mission_rect1 = mission_surf1.get_rect(center=(X_CENTRE, Y_CENTRE-100))
            mission_rect2 = mission_surf2.get_rect(center=(X_CENTRE, Y_CENTRE-42))
            star_rect     = mission_surf2.get_rect(center=(X_CENTRE-100, Y_CENTRE+125))
            clock_surf    = self.fonts["body"].render("Mission time: " + self.game.gametime(), True, ("#FEFEFE"))
            clock_rect    = clock_surf.get_rect(center=(X_CENTRE, Y_CENTRE+100))
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
                if result:
                    self.game.screen.blit(star_surf, star_rect)
                    if self.game.health:
                        for i in range(self.game.health):
                            self.game.screen.blit(self.game.star_img, (X_CENTRE + 100 - (69 + i * 40), Y_CENTRE + 120))
            pygame.display.flip()
            dt = self.game.clock.tick(30) / 1000
            t += dt

    def stats_menu(self):
        viewing_stats = True
        
        title_font = self.fonts["highlight"]  
        label_font = self.fonts["body"]       
        value_font = self.fonts["caption"]    
        back_font  = self.fonts["body"]       
        grid_font  = self.fonts["caption"]    # For the car selection grid items

        WIDTH    = self.game.screen.get_width()
        HEIGHT   = self.game.screen.get_height()
        X_CENTRE = WIDTH // 2

        inspect_idx = getattr(self.game, 'current_car_idx', 0)

        spin_angle  = 0.0
        spin_speed  = 3.0
        last_car_key = None

        back_btn   = pygame.Rect(20, HEIGHT - 70, 160, 50)
        left_panel = pygame.Rect(40, HEIGHT // 5, WIDTH // 2 - 60, HEIGHT // 2 - 20)

        grid_rects   = []
        grid_start_x = 40
        grid_start_y = left_panel.bottom + 20
        grid_item_w  = (left_panel.width - 20) // 3
        grid_item_h  = 35

        for r in range(3):
            for c in range(3):
                idx = r * 3 + c
                if idx < len(self.game.car_options):
                    bx = grid_start_x + c * (grid_item_w + 10)
                    by = grid_start_y + r * (grid_item_h + 8)
                    grid_rects.append((idx, pygame.Rect(bx, by, grid_item_w, grid_item_h)))

        stats_x   = WIDTH // 2 + 40
        stats_y   = HEIGHT // 5 + 10
        row_gap   = 75
        bar_max_w = 260
        bar_h     = 16

        while viewing_stats:
            self.game.screen.fill("#1a252f")
            mouse_pos = pygame.mouse.get_pos()

            car_key    = self.game.car_options[inspect_idx]
            clean_name = car_key.replace("_", " ").title()

            if car_key != last_car_key:
                spin_angle  = 0.0
                last_car_key = car_key

            spin_angle = (spin_angle + spin_speed) % 360.0

            car_stats = getattr(self.game, 'car_stats_database', {}).get(
                car_key, {"speed": 50, "control": 50, "lives": 3, "auto_align": 50})

            stat_rows = [
                {"label": "Speed",   "val": car_stats["speed"],   "max": 100, "color": (231, 76, 60),  "type": "bar"},
                {"label": "Control", "val": car_stats["control"], "max": 100, "color": (52, 152, 219),  "type": "bar"},
                {"label": "Lives",   "val": car_stats["lives"],   "max": 5,   "color": (46, 204, 113),  "type": "stars"},
            ]

            title_surf = title_font.render("VEHICLE REPOSITORY STATS", True, (255, 215, 0))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, 45)))

            pygame.draw.rect(self.game.screen, (44, 62, 80), left_panel, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), left_panel, 2, border_radius=12)

            car_img    = self.game.assets.get_image(car_key)
            scaled_img = pygame.transform.scale(car_img, (int(car_img.get_width() * 1.4), int(car_img.get_height() * 1.4)))

            rotated_img  = pygame.transform.rotate(scaled_img, spin_angle)
            rotated_rect = rotated_img.get_rect(center=(left_panel.centerx, left_panel.centery - 15))
            self.game.screen.blit(rotated_img, rotated_rect)

            name_surf = label_font.render(clean_name, True, (255, 255, 255))
            self.game.screen.blit(name_surf, name_surf.get_rect(center=(left_panel.centerx, left_panel.bottom - 25)))

            for idx, r_box in grid_rects:
                btn_car_key = self.game.car_options[idx]
                btn_name    = btn_car_key.replace("_", " ").title()

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

                val_str  = f"{row['val']}/{row['max']}" if row['type'] != "stars" else f"{row['val']} HP"
                val_surf = value_font.render(val_str, True, (200, 200, 200))
                self.game.screen.blit(val_surf, (stats_x + bar_max_w - val_surf.get_width(), curr_y + 4))

                if row["type"] == "bar":
                    track = pygame.Rect(stats_x, curr_y + 50, bar_max_w, bar_h)
                    pygame.draw.rect(self.game.screen, (30, 39, 46), track, border_radius=6)

                    fill_w    = int(bar_max_w * (row["val"] / row["max"]))
                    fill_rect = pygame.Rect(stats_x, curr_y + 50, fill_w, bar_h)
                    pygame.draw.rect(self.game.screen, row["color"], fill_rect, border_radius=6)

                elif row["type"] == "stars":
                    star_img  = self.game.assets.get_image('star')
                    star_img  = pygame.transform.scale(star_img, (35, 35))
                    star_spacing = 40
                    for star_idx in range(row["val"]):
                        sx = stats_x + (star_idx * star_spacing)
                        sy = curr_y + 40
                        self.game.screen.blit(star_img, (sx, sy))

            align_y  = stats_y + (3 * row_gap)

            align_lbl = label_font.render("Auto Align", True, (255, 255, 255))
            self.game.screen.blit(align_lbl, (stats_x, align_y))

            is_on       = car_stats["auto_align"]
            status_text = "ON" if is_on else "OFF"
            status_color= (46, 204, 113) if is_on else (231, 76, 60)

            status_surf = label_font.render(status_text, True, status_color)
            self.game.screen.blit(status_surf, (stats_x  , align_y + 35))

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


class VolumeSlider:
    def __init__(self, x, y, width, height, initial_val=0.5):
        self.track_rect = pygame.Rect(x, y, width, height)
        self.value      = initial_val
        self.knob_w     = 16
        self.knob_h     = height + 10
        self.dragging   = False
        self.update_knob_from_value()

    def update_knob_from_value(self):
        percentage    = self.value
        knob_center_x = self.track_rect.x + (percentage * self.track_rect.width)
        self.knob_rect = pygame.Rect(
            knob_center_x - self.knob_w // 2,
            self.track_rect.centery - self.knob_h // 2,
            self.knob_w,
            self.knob_h
        )

    def draw(self, screen):
        pygame.draw.rect(screen, (44, 62, 80), self.track_rect, border_radius=4)
        filled_width = self.knob_rect.centerx - self.track_rect.x
        if filled_width > 0:
            filled_rect = pygame.Rect(self.track_rect.x, self.track_rect.y, filled_width, self.track_rect.height)
            pygame.draw.rect(screen, (255, 215, 0), filled_rect, border_radius=4)

        mouse_pos  = pygame.mouse.get_pos()
        knob_color = (52, 152, 219) if (self.knob_rect.collidepoint(mouse_pos) or self.dragging) else (127, 140, 141)
        pygame.draw.rect(screen, knob_color, self.knob_rect, border_radius=4)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.track_rect.x, min(event.pos[0], self.track_rect.right))
                self.knob_rect.centerx = new_x
                self.value = (new_x - self.track_rect.x) / self.track_rect.width
                return True
        return False