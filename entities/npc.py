# npc = non player car
import pygame
from settings import *
from systems.powerups import *

FOLLOW_DISTANCE = 220
FRICTION = 4
ACCELERATION = 2

TRUNK_ICON_OFFSET_Y = 10
TRUNK_ICON_SIZE = 50

class Npc(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y, speed, lane_index, dir):
        super().__init__()

        self.game       = game
        self.image      = image
        self.base_image = image
        self.rect       = self.image.get_rect(center=(x, y))
        self.speed      = speed
        self.target_speed = speed
        self.lane_index = lane_index
        self.dir        = dir
        self.world_x    = x
        self.world_y    = y
        self.hitbox     = None
        self.boom       = None
        self.angle      = 0

        self.powerup = weighted_random_powerup()
        self.has_powerup = self.powerup is not None

        self._icon_surf = self._build_icon_surf()

    def _build_icon_surf(self):
        """Return a scaled icon surface for this NPC's powerup, or None."""
        if not self.has_powerup:
            return None

        info = POWERUP_TYPES.get(self.powerup)
        if info is None or info["icon"] is None:
            return None

        try:
            raw = self.game.assets.get_image(info["icon"])
        except (KeyError, AttributeError):
            # Asset not loaded yet – fall back to a coloured square placeholder.
            raw = pygame.Surface((TRUNK_ICON_SIZE, TRUNK_ICON_SIZE), pygame.SRCALPHA)
            raw.fill(info["color"] + (220,))   # (R,G,B,A)
            return raw

        return pygame.transform.smoothscale(raw, (TRUNK_ICON_SIZE, TRUNK_ICON_SIZE))

    def trunk_position(self):
        """
        Return the (cx, cy) screen position of the trunk icon.

        'Down'-travelling NPCs face downward (sprite top = car front),
        so the trunk is near the sprite's *top* edge on screen.
        'Up'-travelling NPCs are flipped 180°, trunk is near the *bottom*.
        """
        cx = self.rect.centerx
        if self.dir == "down":
            cy = self.rect.top + TRUNK_ICON_OFFSET_Y + TRUNK_ICON_SIZE // 2
        else:
            cy = self.rect.bottom - TRUNK_ICON_OFFSET_Y - TRUNK_ICON_SIZE // 2
        return (cx, cy)

    def update(self, dt):
        if self.boom:
            self.yeet(self.boom)
            return
        car_ahead, distance = self.get_car_ahead()
        apparent_speed = self.speed - self.game.playerspeed

        if car_ahead and distance < FOLLOW_DISTANCE:
            self.speed += (
                car_ahead.speed - self.speed
            ) * FRICTION * dt
        else:
            self.speed += (
                self.target_speed - self.speed
            ) * ACCELERATION * dt

        self.world_y += apparent_speed * dt
        self.rect.center = (self.world_x, self.world_y)
        self.hitbox = self.rect.inflate(-HITBOX_TOLERANCE, -HITBOX_TOLERANCE)

        self.angle = 180 if self.speed > 0 else 0
        self.image = pygame.transform.rotate(self.base_image, self.angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.kill()

    def draw_powerup_icon(self, surface):
        """
        Called by the game's draw() loop (after all_sprites.draw) so the icon
        always renders on top of the car sprite.
        """
        if not self.has_powerup or self._icon_surf is None:
            return

        cx, cy = self.trunk_position()
        icon_rect = self._icon_surf.get_rect(center=(cx, cy))
        surface.blit(self._icon_surf, icon_rect)

    def try_steal(self, player_rect):
        """
        Returns the stolen powerup key if:
          - the player's *full* rect (not hitbox) overlaps this NPC's rect, AND
          - this NPC still has a powerup.

        The caller is responsible for consuming the returned value.
        Passing the full player_rect (not the hitbox) means the player can
        just barely touch the car visually without triggering the hitbox damage.
        """
        if not self.has_powerup:
            return None

        if player_rect.colliderect(self.rect):
            stolen          = self.powerup
            self.powerup    = None
            self.has_powerup = False
            self._icon_surf  = None   # hide icon immediately
            return stolen

        return None

    def get_car_ahead(self):
        nearest_car      = None
        nearest_distance = float("inf")

        for npc in self.game.npcs:
            if npc == self:
                continue
            if npc.lane_index != self.lane_index:
                continue
            if npc.dir != self.dir:
                continue

            distance = npc.world_y - self.world_y

            if self.dir == "down":
                if distance <= 0:
                    continue
            elif self.dir == "up":
                if distance >= 0:
                    continue
                distance = abs(distance)

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_car      = npc

        return nearest_car, nearest_distance
    
    def yeet(self, origin):
        dx = origin["origin_x"] - self.world_x
        dy = origin["origin_y"] - self.world_y
        self.hitbox = None
        self.world_x -= BLAST_POWER * dx / dy
        self.world_y -= BLAST_POWER * dy / dx
        self.rect.center = (self.world_x, self.world_y)
        self.angle += 2 * dy / dx
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        if (
            self.world_x < -200 or self.world_x > WIDTH+200 
            or self.world_y < -200 or self.world_y > HEIGHT+200
        ):
            self.kill()
