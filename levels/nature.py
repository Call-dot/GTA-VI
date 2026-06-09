import random
from settings import *
from levels.biomes import BIOMES

class Nature:
    def __init__(self, game, seed):
        super().__init__()
        self.game = game
        self.random = random.Random(seed)

    def scenery_generator(self, type="tree"):
        """Generate random scenery objects for the current biome"""
        biome_key = self.game.current_biome
        data = BIOMES[biome_key]
        generated_scenery = []

        if type == "tree":
            count = int(WIDTH * HEIGHT * data["tree_density"] * 0.00005)
            tree_images = [
                img for img in data["background_images"]
                if "tree" in img or "palm" in img
            ]
            if tree_images:
                for _ in range(count):
                    img = self.random.choice(tree_images)
                    x = self.random.randint(0, WIDTH)
                    y = self.random.randint(300, 550)
                    generated_scenery.append({"image": img, "x": x, "y": y})

        elif type == "rocks":
            count = int(WIDTH * HEIGHT * data["rock_density"] * 0.00005)
            rock_images = [
                img for img in data["background_images"]
                if "rock" in img or "stone" in img
            ]
            if rock_images:
                for _ in range(count):
                    img = self.random.choice(rock_images)
                    x = self.random.randint(0, WIDTH)
                    y = self.random.randint(400, 580)
                    generated_scenery.append({"image": img, "x": x, "y": y})

        return generated_scenery

    def scenery_tiler(self):
        """
        Mirrors bg_tiler() — scrolls scenery objects with the world and
        generates new ones as the player moves forward.
        Trees saved to self.trees, rocks to self.rocks.
        """
        # Shift existing scenery up as the world scrolls
        offset = self.game.playerspeed * self.game.dt

        for obj in self.game.trees:
            obj["y"] -= offset  # objects scroll upward as player drives

        for obj in self.game.rocks:
            obj["y"] -= offset

        # Cull objects that have scrolled off the top of the screen
        self.game.trees = [obj for obj in self.game.trees if obj["y"] > -100]
        self.game.rocks = [obj for obj in self.game.rocks if obj["y"] > -100]

        # Spawn new scenery at the bottom as we scroll
        # Tie spawn rate loosely to player speed so faster = more variety
        spawn_chance = self.game.playerspeed * self.game.dt * 0.05

        if self.random.random() < spawn_chance:
            new_trees = self.scenery_generator("tree")
            for obj in new_trees:
                obj["y"] = HEIGHT + self.random.randint(0, 100)  # spawn below screen
            self.game.trees.extend(new_trees)

        if self.random.random() < spawn_chance * 0.5:  # rocks are rarer
            new_rocks = self.scenery_generator("rocks")
            for obj in new_rocks:
                obj["y"] = HEIGHT + self.random.randint(0, 100)
            self.game.rocks.extend(new_rocks)
