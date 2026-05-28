import random
from levels.roads import ROAD_TYPES


class Tiler:
    def __init__(self, seed=None):
        self.random = random.Random(seed)

        self.current_road = None
        self.rows_remaining = 0

        self.choose_new_road()

    def choose_new_road(self):
        road_names = list(ROAD_TYPES.keys())

        weights = [
            ROAD_TYPES[name]["weight"]
            for name in road_names
        ]

        chosen_name = self.random.choices(
            road_names,
            weights=weights,
            k=1
        )[0]

        self.current_road = ROAD_TYPES[chosen_name]

        self.rows_remaining = self.random.randint(
            self.current_road["min_length"],
            self.current_road["max_length"]
        )

    def next_row(self):
        if self.rows_remaining <= 0:
            self.choose_new_road()

        self.rows_remaining -= 1

        return {
            "layout": self.current_road["layout"],
            "lanes": self.current_road["lanes"],
            "road_type": self.current_road,
        }