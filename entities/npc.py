# npc = non player car
import pygame

FOLLOW_DISTANCE = 220
FRICTION = 4
ACCELERATION = 2

class Npc(pygame.sprite.Sprite):
    def __init__(self, game, image, x, y, speed, lane_index, dir):
        super().__init__()

        self.game = game
        self.image = image
        self.base_image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.target_speed = speed
        self.lane_index = lane_index
        self.dir = dir
        self.world_x = x
        self.world_y = y


    def update(self, dt):
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

        angle = 180 if self.speed > 0 else 0
        self.image = pygame.transform.rotate(self.base_image, angle)

        # delete when offscreen
        if self.rect.top > self.game.height + 169:
            self.kill()

    def get_car_ahead(self):
        nearest_car = None
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
                nearest_car = npc

        return nearest_car, nearest_distance