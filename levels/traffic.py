import random
from levels.roads import ROAD_TYPES
from settings import *

class Tiler:
    def __init__(self, game, seed=None, driving_side="right"):
        self.random = random.Random(seed)
        self.driving_side = driving_side
        print(self.driving_side) #debug
        self.current_road = None
        self.rows_remaining = 0
        self.intersecting = False
        self.intersection = []
        self.signal = True
        self.signaltimer = 0
        self.game = game
        self.t = self.game.t

        self.choose_new_road()

    def choose_new_road(self):
        road_names = list(ROAD_TYPES.keys())

        weights = [ROAD_TYPES[name]["weight"] for name in road_names]

        chosen_name = self.random.choices(road_names, weights=weights, k=1)[0]

        self.current_road = ROAD_TYPES[chosen_name]

        self.rows_remaining = self.random.randint(self.current_road["min_length"], self.current_road["max_length"])

    def next_row(self):
        if self.rows_remaining <= 0 or self.intersection:
            if not self.intersection:
                exit_rows = self.exit()
                print("OG road:", self.current_road["layout"], exit_rows)
                self.choose_new_road()
                entrance_rows = self.entrance()
                print("new road:", self.current_road["layout"], entrance_rows)
                self.intersecting = True
                sideroad_size = random.choice([1, 3, 5])
                print(sideroad_size)
                self.intersection.extend(exit_rows)
                self.intersection.extend(self.sideroad(sideroad_size))
                self.intersection.extend(entrance_rows)

            print(self.intersection)
            layout = self.intersection.pop(0)

            return {
                "layout": layout,
                "lanes": self.resolve_lanes(self.current_road),
                "road_type": self.current_road
            }

        self.rows_remaining -= 1
        # British driving
        resolved_lanes = self.resolve_lanes(self.current_road)

        return {
            "layout": self.current_road["layout"],
            "lanes": resolved_lanes,
            "road_type": self.current_road
        }
    
    def sideroad(self, size=5):
        road = ["`+" * (int(HEIGHT // ROAD_SIZE_X)) + "`" for _ in range(size)]
        temp_list = list(road[size // 2])
        temp_list[len(temp_list)//2] = '%'
        road[size // 2] = "".join(temp_list)
        return road
    
    def entrance(self):
        return self.random.choice(self.current_road["entrances"])

    def exit(self):
        return self.random.choice(self.current_road["exits"])

    def resolve_lanes(self, road):
        resolved_lanes = {}

        for lane_index, lane_data in road["lanes"].items():
            lane_copy = lane_data.copy()

            if lane_copy["dir"] == "down":
                lane_copy["dir"] = (
                    "down" if self.driving_side == "right" else "up"
                )

            elif lane_copy["dir"] == "up":
                lane_copy["dir"] = (
                    "up" if self.driving_side == "right" else "down"
                )

            resolved_lanes[lane_index] = lane_copy

        return resolved_lanes
    
    def signals(self):
        if self.signaltimer <= 0:
            self.signaltimer = self.random.randrange(MIN_LIGHT_TIME, MAX_LIGHT_TIME)
            self.signal = not self.signal
        else:
            self.signaltimer -= self.game.dt
            # print("RED LIGHT:", self.signal, "TIME LEFT:", self.signaltimer)
        return self.signal, self.signaltimer