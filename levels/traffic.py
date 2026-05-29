import random
from levels.roads import ROAD_TYPES

class Tiler:
    def __init__(self, seed=None, driving_side="right"):
        self.random = random.Random(seed)
        self.driving_side = driving_side
        print(self.driving_side) #debug
        self.current_road = None
        self.rows_remaining = 0

        self.choose_new_road()

    def choose_new_road(self):
        road_names = list(ROAD_TYPES.keys())

        weights = [ROAD_TYPES[name]["weight"] for name in road_names]

        chosen_name = self.random.choices(road_names, weights=weights, k=1)[0]

        self.current_road = ROAD_TYPES[chosen_name]

        self.rows_remaining = self.random.randint(self.current_road["min_length"], self.current_road["max_length"])

    def next_row(self):
        if self.rows_remaining <= 0:
            self.choose_new_road()

        self.rows_remaining -= 1

        # British driving
        resolved_lanes = {}
        for lane_index, lane_data in self.current_road["lanes"].items():
            lane_copy = lane_data.copy()

            if lane_copy["dir"] == "down":
                lane_copy["dir"] = ("down" if self.driving_side == "right" else "up")

            elif lane_copy["dir"] == "up":
                lane_copy["dir"] = ("up" if self.driving_side == "right" else "down")

            resolved_lanes[lane_index] = lane_copy

        return {
            "layout": self.current_road["layout"],
            "lanes": resolved_lanes,
            "road_type": self.current_road,
        }