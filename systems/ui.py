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
from profile import (
    load_profile, save_profile, save_settings, apply_settings,
    try_purchase, CAR_PRICES,
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
            self.game.vlc("title", -1, False)
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

                load_text = self.fonts["body"].render("DEALERSHIP", True, (255, 255, 255))
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
                            self.shop_menu()

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

        box_w, box_h = 540, 320
        popup_rect = pygame.Rect(X_CENTRE - box_w // 2, Y_CENTRE - box_h // 2, box_w, box_h)

        btn_w, btn_h = 380, 55
        continue_btn = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE - 5, btn_w, btn_h)
        exit_btn     = pygame.Rect(X_CENTRE - btn_w // 2, Y_CENTRE + 65, btn_w, btn_h)

        while paused:
            mouse_pos = pygame.mouse.get_pos()
            
            pygame.draw.rect(self.game.screen, (30, 43, 56), popup_rect, border_radius=12)
            pygame.draw.rect(self.game.screen, (255, 215, 0), popup_rect, 2, border_radius=12) # Gold border

            title_surf = self.fonts["header"].render("GAME PAUSED", True, (255, 255, 255))
            self.game.screen.blit(title_surf, title_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 90)))

            continue_color = (0, 200, 100) if continue_btn.collidepoint(mouse_pos) else (44, 62, 80)
            exit_color     = (200, 50, 50)  if exit_btn.collidepoint(mouse_pos)     else (44, 62, 80)

            pygame.draw.rect(self.game.screen, continue_color, continue_btn, border_radius=6)
            pygame.draw.rect(self.game.screen, exit_color, exit_btn, border_radius=6)

            cont_txt = self.fonts["body"].render("CONTINUE", True, (255, 255, 255))
            self.game.screen.blit(cont_txt, cont_txt.get_rect(center=continue_btn.center))

            exit_txt = self.fonts["body"].render("EXIT TO MENU", True, (255, 255, 255))
            self.game.screen.blit(exit_txt, exit_txt.get_rect(center=exit_btn.center))

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

        g.end_run()


    # SHOP

    def shop_menu(self):
        """
        Car shop.  Displays all cars in a grid with prices.
        Owned cars are shown with a green "OWNED" badge.
        Affordable cars can be purchased via a confirmation popup.
        Unaffordable cars show a red "NEED X ★" label.
        Respect counter shown top-right.
        """
        profile  = self.game.profile
        all_cars = self.game.car_options   # full roster regardless of unlock state

        # layout 
        W, H     = self.game.screen.get_size()
        XC, YC   = W // 2, H // 2
        PAD      = 20
        CARD_W, CARD_H = 155, 190
        COLS     = 5
        ROWS     = math.ceil(len(all_cars) / COLS)
        grid_w   = COLS * CARD_W + (COLS - 1) * PAD
        grid_x0  = XC - grid_w // 2
        grid_y0  = 100

        # ── colours ───────────────────────────────────────────────────────────
        BG         = (20, 25, 30)
        CARD_IDLE  = (34, 47, 62)
        CARD_HOV   = (52, 73, 94)
        OWNED_COL  = (39, 174, 96)
        CANT_COL   = (180, 60, 60)
        BUY_COL    = (41, 128, 185)
        ACCENT     = (255, 215, 0)
        TEXT_W     = (255, 255, 255)
        TEXT_DIM   = (149, 165, 166)

        f_title  = self.fonts["header"]
        f_body   = self.fonts["body"]
        f_small  = self.fonts["caption"]

        back_btn = pygame.Rect(PAD, H - PAD - 50, 160, 50)

        star_raw  = self.game.assets.get_image("star")
        star_sm   = pygame.transform.smoothscale(star_raw, (22, 22))
        star_lg   = pygame.transform.smoothscale(star_raw, (28, 28))

        def card_rect(idx):
            col = idx % COLS
            row = idx // COLS
            x   = grid_x0 + col * (CARD_W + PAD)
            y   = grid_y0 + row * (CARD_H + PAD)
            return pygame.Rect(x, y, CARD_W, CARD_H)

        def draw():
            self.game.screen.fill(BG)
            mouse = pygame.mouse.get_pos()

            # title 
            t_surf = f_title.render("DEALERSHIP", True, ACCENT)
            self.game.screen.blit(t_surf, t_surf.get_rect(midtop=(XC, 16)))

            # respect counter (top-right)
            resp   = profile["respect"]
            r_lbl  = f_body.render("RESPECT:", True, TEXT_DIM)
            r_num  = f_body.render(str(resp), True, ACCENT)
            rx     = W - PAD - star_lg.get_width() - 6 - r_num.get_width() - 8 - r_lbl.get_width()
            ry     = 20
            self.game.screen.blit(r_lbl, (rx, ry))
            self.game.screen.blit(r_num, (rx + r_lbl.get_width() + 8, ry))
            self.game.screen.blit(star_lg, (rx + r_lbl.get_width() + 8 + r_num.get_width() + 6,
                                            ry - 2))

            # car cards 
            for idx, car_key in enumerate(all_cars):
                r      = card_rect(idx)
                owned  = car_key in profile["unlocked_cars"]
                price  = CAR_PRICES.get(car_key, 0)
                can_buy= (not owned) and profile["respect"] >= price
                hov    = r.collidepoint(mouse)

                bg_col = CARD_HOV if hov else CARD_IDLE
                pygame.draw.rect(self.game.screen, bg_col, r, border_radius=10)

                # border: gold if hovered, green if owned
                if owned:
                    pygame.draw.rect(self.game.screen, OWNED_COL, r, 2, border_radius=10)
                elif hov:
                    pygame.draw.rect(self.game.screen, ACCENT, r, 2, border_radius=10)

                # car image
                try:
                    ci     = self.game.assets.get_image(car_key)
                    thumb  = pygame.transform.smoothscale(ci, (90, 90))
                    self.game.screen.blit(thumb, thumb.get_rect(center=(r.centerx, r.y + 60)))
                except Exception:
                    pass

                # name
                name_s = f_small.render(car_key.replace("_", " ").title(), True, TEXT_W)
                self.game.screen.blit(name_s, name_s.get_rect(center=(r.centerx, r.y + 115)))

                # status badge
                if owned:
                    badge  = f_small.render("OWNED", True, OWNED_COL)
                    self.game.screen.blit(badge, badge.get_rect(center=(r.centerx, r.y + 140)))
                elif price == 0:
                    badge  = f_small.render("FREE", True, ACCENT)
                    self.game.screen.blit(badge, badge.get_rect(center=(r.centerx, r.y + 140)))
                else:
                    # price with star icon
                    p_surf = f_small.render(str(price), True,
                                            BUY_COL if can_buy else CANT_COL)
                    total_w = p_surf.get_width() + star_sm.get_width() + 4
                    bx = r.centerx - total_w // 2
                    by = r.y + 133
                    self.game.screen.blit(p_surf, (bx, by + 2))
                    self.game.screen.blit(star_sm, (bx + p_surf.get_width() + 4, by))

                # "click to buy" hint
                if hov and not owned and can_buy:
                    hint = f_small.render("Click to buy", True, ACCENT)
                    self.game.screen.blit(hint, hint.get_rect(center=(r.centerx, r.bottom - 14)))
                elif hov and not owned and not can_buy:
                    needed = price - profile["respect"]
                    hint = f_small.render(f"Need {needed} more ★", True, CANT_COL)
                    self.game.screen.blit(hint, hint.get_rect(center=(r.centerx, r.bottom - 14)))

            # back button 
            bc = (100, 110, 120) if not back_btn.collidepoint(mouse) else (140, 150, 160)
            pygame.draw.rect(self.game.screen, bc, back_btn, border_radius=7)
            bt = f_body.render("< BACK", True, TEXT_W)
            self.game.screen.blit(bt, bt.get_rect(center=back_btn.center))

            pygame.display.flip()

        # confirm purchase
        def confirm_purchase(car_key: str) -> bool:
            price    = CAR_PRICES.get(car_key, 0)
            name     = car_key.replace("_", " ").title()
            pop_w, pop_h = 420, 220
            pop_r    = pygame.Rect(XC - pop_w // 2, YC - pop_h // 2, pop_w, pop_h)
            bw, bh   = 130, 48
            yes_btn  = pygame.Rect(pop_r.centerx - bw - 15, pop_r.bottom - bh - 24, bw, bh)
            no_btn   = pygame.Rect(pop_r.centerx + 15,       pop_r.bottom - bh - 24, bw, bh)

            while True:
                mouse = pygame.mouse.get_pos()
                draw()   # keep shop visible behind the overlay

                overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.game.screen.blit(overlay, (0, 0))

                pygame.draw.rect(self.game.screen, (34, 47, 62), pop_r, border_radius=12)
                pygame.draw.rect(self.game.screen, ACCENT, pop_r, 2, border_radius=12)

                q  = f_body.render(f"Buy {name}?", True, TEXT_W)
                self.game.screen.blit(q, q.get_rect(center=(pop_r.centerx, pop_r.y + 38)))

                # price line with star
                p_surf   = f_body.render(str(price), True, ACCENT)
                cost_lbl = f_small.render("Cost: ", True, TEXT_DIM)
                cx = pop_r.centerx - (cost_lbl.get_width() + p_surf.get_width() + star_sm.get_width() + 6) // 2
                cy = pop_r.y + 80
                self.game.screen.blit(cost_lbl, (cx, cy + 3))
                cx += cost_lbl.get_width()
                self.game.screen.blit(p_surf, (cx, cy))
                cx += p_surf.get_width() + 4
                self.game.screen.blit(star_sm, (cx, cy))

                bal_s = f_small.render(
                    f"Balance after: {profile['respect'] - price} ★", True, TEXT_DIM)
                self.game.screen.blit(bal_s, bal_s.get_rect(center=(pop_r.centerx, pop_r.y + 118)))

                yc = OWNED_COL if yes_btn.collidepoint(mouse) else (30, 120, 60)
                nc = (150, 50, 50) if no_btn.collidepoint(mouse) else (80, 30, 30)
                pygame.draw.rect(self.game.screen, yc, yes_btn, border_radius=7)
                pygame.draw.rect(self.game.screen, nc, no_btn,  border_radius=7)

                self.game.screen.blit(
                    f_body.render("BUY", True, TEXT_W),
                    f_body.render("BUY", True, TEXT_W).get_rect(center=yes_btn.center))
                self.game.screen.blit(
                    f_body.render("CANCEL", True, TEXT_W),
                    f_body.render("CANCEL", True, TEXT_W).get_rect(center=no_btn.center))

                pygame.display.flip()
                self.game.clock.tick(30)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if yes_btn.collidepoint(event.pos):
                            return True
                        if no_btn.collidepoint(event.pos):
                            return False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return False

        def cant_afford_popup(car_key: str):
            price  = CAR_PRICES.get(car_key, 0)
            name   = car_key.replace("_", " ").title()
            needed = price - profile["respect"]
            pop_w, pop_h = 380, 170
            pop_r  = pygame.Rect(XC - pop_w // 2, YC - pop_h // 2, pop_w, pop_h)
            ok_btn = pygame.Rect(pop_r.centerx - 60, pop_r.bottom - 58, 120, 40)

            while True:
                mouse = pygame.mouse.get_pos()
                draw()
                overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.game.screen.blit(overlay, (0, 0))

                pygame.draw.rect(self.game.screen, (50, 20, 20), pop_r, border_radius=12)
                pygame.draw.rect(self.game.screen, CANT_COL, pop_r, 2, border_radius=12)

                h1 = f_body.render("Can't afford!", True, CANT_COL)
                self.game.screen.blit(h1, h1.get_rect(center=(pop_r.centerx, pop_r.y + 38)))
                h2 = f_small.render(f"{name} costs {price} respect  (need {needed} more)", True, TEXT_DIM)
                self.game.screen.blit(h2, h2.get_rect(center=(pop_r.centerx, pop_r.y + 78)))

                oc = (100, 110, 120) if not ok_btn.collidepoint(mouse) else (140, 150, 160)
                pygame.draw.rect(self.game.screen, oc, ok_btn, border_radius=6)
                ok_s = f_body.render("OK", True, TEXT_W)
                self.game.screen.blit(ok_s, ok_s.get_rect(center=ok_btn.center))

                pygame.display.flip()
                self.game.clock.tick(30)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if ok_btn.collidepoint(event.pos):
                            return
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return

        # shop loop
        running = True
        while running:
            draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos

                    if back_btn.collidepoint(pos):
                        running = False
                        continue

                    for idx, car_key in enumerate(all_cars):
                        if not card_rect(idx).collidepoint(pos):
                            continue
                        owned = car_key in profile["unlocked_cars"]
                        if owned:
                            break
                        price   = CAR_PRICES.get(car_key, 0)
                        can_buy = profile["respect"] >= price
                        if not can_buy:
                            cant_afford_popup(car_key)
                        else:
                            if confirm_purchase(car_key):
                                try_purchase(profile, car_key)   # deducts + saves
                        break

            self.game.clock.tick(30)

    def settings_menu(self):
        """Settings: volume slider, fullscreen, show hitboxes, driving side."""
        in_settings = True
        profile = self.game.profile

        WIDTH  = self.game.screen.get_width()
        HEIGHT = self.game.screen.get_height()
        X_CENTRE, Y_CENTRE = WIDTH // 2, HEIGHT // 2

        slider_w, slider_h = 300, 12
        volume_slider = VolumeSlider(
            x=X_CENTRE - slider_w // 2,
            y=Y_CENTRE - 90,
            width=slider_w,
            height=slider_h,
            initial_val=pygame.mixer.music.get_volume()
        )

        BTN_W, BTN_H = 420, 50
        bx = X_CENTRE - BTN_W // 2

        fullscreen_btn    = pygame.Rect(bx, Y_CENTRE - 10,  BTN_W, BTN_H)
        hitbox_btn        = pygame.Rect(bx, Y_CENTRE + 55,  BTN_W, BTN_H)
        driving_side_btn  = pygame.Rect(bx, Y_CENTRE + 120, BTN_W, BTN_H)
        back_btn          = pygame.Rect(20, HEIGHT - 70,    160,   50)

        # colours
        IDLE  = (30, 43, 56)
        HOV   = (44, 62, 80)
        ON    = (39, 174, 96)   # green  — setting is active
        OFF   = (150, 50, 50)   # red    — setting is inactive

        while in_settings:
            # re-fetch in case window was resized / mode toggled this frame
            WIDTH  = self.game.screen.get_width()
            HEIGHT = self.game.screen.get_height()
            X_CENTRE, Y_CENTRE = WIDTH // 2, HEIGHT // 2

            mouse_pos = pygame.mouse.get_pos()
            self.game.screen.fill("#1B1B1B")

            title_surf = self.fonts["header"].render("SETTINGS", True, (255, 255, 255))
            self.game.screen.blit(title_surf,
                                  title_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 170)))

            vol_pct  = int(volume_slider.value * 100)
            vol_surf = self.fonts["body"].render(f"MUSIC VOLUME: {vol_pct}%",
                                                 True, (255, 255, 255))
            self.game.screen.blit(vol_surf,
                                  vol_surf.get_rect(center=(X_CENTRE, Y_CENTRE - 128)))
            volume_slider.draw(self.game.screen)

            def draw_toggle(rect, label, state: bool):
                hov   = rect.collidepoint(mouse_pos)
                color = (ON if state else OFF) if not hov else HOV
                pygame.draw.rect(self.game.screen, color, rect, border_radius=6)
                state_tag = "  [ON]" if state else "  [OFF]"
                txt = self.fonts["body"].render(label + state_tag, True, (255, 255, 255))
                self.game.screen.blit(txt, txt.get_rect(center=rect.center))

            is_fs = getattr(self.game, "is_fullscreen", False)
            draw_toggle(fullscreen_btn, "FULLSCREEN", is_fs)

            show_hb = getattr(self.game, "show_hitboxes", False)
            draw_toggle(hitbox_btn, "SHOW HITBOXES", show_hb)

            british = getattr(self.game, "british_driving", False)
            side_label = "DRIVE ON: LEFT" if british else "DRIVE ON: RIGHT"
            hov = driving_side_btn.collidepoint(mouse_pos)
            ds_col = (44, 62, 80) if hov else (30, 43, 56)
            pygame.draw.rect(self.game.screen, ds_col, driving_side_btn, border_radius=6)
            ds_surf = self.fonts["body"].render(side_label, True, (255, 255, 255))
            self.game.screen.blit(ds_surf,
                                  ds_surf.get_rect(center=driving_side_btn.center))

            back_bg = HOV if back_btn.collidepoint(mouse_pos) else IDLE
            pygame.draw.rect(self.game.screen, back_bg, back_btn, border_radius=6)
            back_text = self.fonts["body"].render("< BACK", True, (255, 255, 255))
            self.game.screen.blit(back_text, back_text.get_rect(center=back_btn.center))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if volume_slider.handle_event(event):
                    pygame.mixer.music.set_volume(volume_slider.value)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if fullscreen_btn.collidepoint(event.pos):
                        if is_fs:
                            self.game.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            self.game.is_fullscreen = False
                        else:
                            info = pygame.display.Info()
                            self.game.screen = pygame.display.set_mode(
                                (info.current_w, info.current_h),
                                pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                            )
                            self.game.is_fullscreen = True

                    elif hitbox_btn.collidepoint(event.pos):
                        self.game.show_hitboxes = not getattr(
                            self.game, "show_hitboxes", False)

                    elif driving_side_btn.collidepoint(event.pos):
                        self.game.british_driving = not getattr(
                            self.game, "british_driving", False)
                        # Mirror onto the tiler so it takes effect next new game
                        self.game.tiler.driving_side = (
                            "left" if self.game.british_driving else "right"
                        )

                    elif back_btn.collidepoint(event.pos):
                        save_settings(profile, self.game)
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
        spacing_x, spacing_y = 30, 30

        # Only show cars the player has unlocked
        unlocked = self.game.profile.get("unlocked_cars", [self.game.car_options[0]])
        available_cars = [c for c in self.game.car_options if c in unlocked]
        if not available_cars:
            available_cars = [self.game.car_options[0]]

        row1_count = min(5, len(available_cars))
        row1_start_x = X_CENTRE - ((card_w * row1_count + spacing_x * (row1_count - 1)) / 2)
        row1_y = Y_CENTRE - card_h - (spacing_y / 2)

        row2_count = max(0, len(available_cars) - 5)
        row2_start_x = X_CENTRE - ((card_w * row2_count + spacing_x * (max(row2_count - 1, 0))) / 2)
        row2_y = Y_CENTRE + (spacing_y / 2)

        self.game.music[1] = False
        self.game.vlc("menu", -1, False)

        rects = []
        for idx in range(len(available_cars)):
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
            welcome_rect = welcome_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 0.6))
            self.game.screen.blit(welcome_surf, welcome_rect)

            title_surf = self.fonts["header"].render("PICK YOUR RIDE", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(X_CENTRE, HEIGHT // 8 * 1.2))
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
                car_surface = self.game.assets.get_image(available_cars[idx])
                car_rect    = car_surface.get_rect(center=(rect.centerx, rect.centery - 15))
                self.game.screen.blit(car_surface, car_rect)

                clean_name = available_cars[idx].replace("_", " ").title()
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
                            chosen_key = available_cars[idx]
                            self.game.player_model = chosen_key
                            self.game.player_img   = self.game.assets.get_image(chosen_key)
                            self.game.current_car_idx = idx
                            self.game.playerdata = self.game.stat_presets[chosen_key]
                            self.game.max_speed = MAX_SPEED * (self.game.playerdata["speed"] / 100 + 0.3)
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
        """
        GTA-style mission end card.
        Title -> subtitle -> Stats
        """
        result = respect
        W = self.game.screen.get_width()
        H = self.game.screen.get_height()
        XC, YC = W // 2, H // 2
 
        # ── colours ───────────────────────────────────────────────────────────
        GOLD      = (212, 175, 55)
        WHITE     = (255, 255, 255)
        DIM       = (190, 190, 190)
        RULE_COL  = (200, 200, 200)
        FAIL_COL  = (200, 60, 60)
 
        title_col = GOLD if result else FAIL_COL
 
        # ── panel geometry ────────────────────────────────────────────────────
        PANEL_W  = 420
        ROW_H    = 36       # height of each stat row
        ROW_GAP  = 2
        PADDING  = 24
 
        # stat rows: (label, value_string | None-for-stars)
        mission_time = self.game.gametime()
        chased       = getattr(self.game, "chased", False)
        health       = self.game.health if result else 0
 
        stat_rows = [
            ("Time Taken",    mission_time),
            ("Clean Run",     "DNF" if not result else ("Yes" if not chased else "No")),
            ("Respect Earned",  "stars"),   # rendered specially
        ]
 
        n_rows    = len(stat_rows)
        PANEL_H   = PADDING + n_rows * (ROW_H + ROW_GAP) + PADDING + ROW_H  # extra row for completion
 
        # vertically position panel below the subtitle
        TITLE_Y    = YC - 130
        SUBTITLE_Y = YC - 65
        PANEL_Y    = SUBTITLE_Y + 34
        PANEL_X    = XC - PANEL_W // 2
 
        panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
 
        # ── star image ────────────────────────────────────────────────────────
        star_raw = self.game.assets.get_image("star")
        star_img = pygame.transform.smoothscale(star_raw, (24, 24))
 
        # ── Continue button (bottom-right, GTA-style) ─────────────────────────
        cont_font = self.fonts["highlight"]
        cont_surf = cont_font.render("Continue  ►", True, WHITE)
        cont_rect = cont_surf.get_rect(bottomright=(W - 28, H - 22))
        key_surf  = self.fonts["caption"].render("[ENTER]", True, DIM)
        key_rect  = key_surf.get_rect(bottomright=(W - 28, cont_rect.top - 4))
 
        # ── animation state ───────────────────────────────────────────────────
        t             = 0.0
        phase         = 0          # 0=title, 1=subtitle, 2=stats+continue
        rows_revealed = 0
        waiting       = False      # True once all rows shown; waiting for click
 
        sfx_played = [False, False, False]   # guards per-phase sfx

        self.game.music[1] = False
        self.game.vlc("outro", 1, False)
 
        while True:
            dt = self.game.clock.tick(30) / 1000
            t += dt
 
            # ── phase transitions ─────────────────────────────────────────────
            if t >= 1.0 and phase == 0:
                phase = 1
            if t >= 2.0 and phase == 1:
                phase = 2
            if phase == 2:
                rows_revealed = min(n_rows, int((t - 2.0) / 0.35) + 1)
                if rows_revealed >= n_rows:
                    waiting = True
 
            # ── sfx ───────────────────────────────────────────────────────────
            if phase >= 0 and not sfx_played[0]:
                self.game.sfx("slap", 1); sfx_played[0] = True
            if phase >= 1 and not sfx_played[1]:
                self.game.sfx("slap", 3); sfx_played[1] = True
            if phase >= 2 and not sfx_played[2]:
                self.game.sfx("slap", 2); sfx_played[2] = True
 
            # ── events ────────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if waiting:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        return
                    if event.type == pygame.KEYDOWN and event.key in (
                            pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        return
 
            # ── draw ──────────────────────────────────────────────────────────
            # semi-transparent dark overlay over whatever is already on screen
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.game.screen.blit(overlay, (0, 0))
 
            # ── TITLE ─────────────────────────────────────────────────────────
            if result:
                title_str = "MiSSiON PaSSeD"
            else:
                title_str = "MiSSiON FaiLeD"
 
            title_surf = self.fonts["bungeeshade"].render(title_str, True, title_col)
            self.game.screen.blit(title_surf,
                                  title_surf.get_rect(center=(XC, TITLE_Y)))
 
            # ── SUBTITLE ──────────────────────────────────────────────────────
            if phase >= 1:
                sub_str  = "Get to school on time!" if result else "You're late!"
                sub_surf = self.fonts["highlight"].render(sub_str, True, WHITE)
                self.game.screen.blit(sub_surf,
                                      sub_surf.get_rect(center=(XC, SUBTITLE_Y)))
 
            # ── STATS PANEL ───────────────────────────────────────────────────
            if phase >= 2:
                # frosted panel background
                panel_surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
                panel_surf.fill((0, 0, 0, 100))
                self.game.screen.blit(panel_surf, panel_rect.topleft)
 
                # top rule line
                pygame.draw.line(self.game.screen, RULE_COL,
                                 (PANEL_X, PANEL_Y),
                                 (PANEL_X + PANEL_W, PANEL_Y), 1)
 
                for i in range(rows_revealed):
                    label, value = stat_rows[i]
                    ry = PANEL_Y + PADDING + i * (ROW_H + ROW_GAP)
 
                    # row rule
                    pygame.draw.line(self.game.screen, (*RULE_COL, 80),
                                     (PANEL_X, ry + ROW_H),
                                     (PANEL_X + PANEL_W, ry + ROW_H), 1)
 
                    # label
                    lbl = self.fonts["body"].render(label, True, WHITE)
                    self.game.screen.blit(lbl, (PANEL_X + 8, ry + (ROW_H - lbl.get_height()) // 2))
 
                    # value
                    if value == "stars":
                        # draw star icons right-aligned
                        sx = PANEL_X + PANEL_W - 8
                        sy = ry + (ROW_H - star_img.get_height()) // 2
                        for _ in range(health):
                            sx -= star_img.get_width() + 4
                            self.game.screen.blit(star_img, (sx, sy))
                        if health == 0:
                            none_s = self.fonts["caption"].render("NONE", True, FAIL_COL)
                            self.game.screen.blit(none_s, none_s.get_rect(
                                midright=(PANEL_X + PANEL_W - 8, ry + ROW_H // 2)))
                    elif value is not None:
                        val_surf = self.fonts["body"].render(str(value), True, DIM)
                        self.game.screen.blit(val_surf, val_surf.get_rect(
                            midright=(PANEL_X + PANEL_W - 8, ry + ROW_H // 2)))
 
                # bottom rule
                bottom_y = PANEL_Y + PADDING + n_rows * (ROW_H + ROW_GAP)
                pygame.draw.line(self.game.screen, RULE_COL,
                                 (PANEL_X, bottom_y),
                                 (PANEL_X + PANEL_W, bottom_y), 1)
 
                # completion row
                comp_pct  = 100 if result else 0
                comp_lbl  = self.fonts["highlight"].render(f"Completion  {comp_pct}%", True, WHITE)
                self.game.screen.blit(comp_lbl,
                                      comp_lbl.get_rect(center=(XC, bottom_y + ROW_H // 2 + 4)))
 
            # ── Continue button ────────────────────────────────────────────────
            if waiting:
                # subtle pulse so player knows it's clickable
                alpha = int(180 + 75 * math.sin(t * 4))
                c_surf = cont_font.render("Continue  ►", True, (*WHITE, alpha))
                self.game.screen.blit(c_surf, cont_rect)
                self.game.screen.blit(key_surf, key_rect)
 
            pygame.display.flip()
 

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