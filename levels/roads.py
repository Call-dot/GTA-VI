ROAD_TYPES = {
    "two_way_two_lane": {
        "layout": "__./.|./.__",

        "lanes": {
            2: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            6: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },
        },

        "traffic": 1.0,
        "weight": 10,
        "min_length": 20,
        "max_length": 60,
    },

    "one_way_two_lane": {
        "layout": "__././.__",

        "lanes": {
            2: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            4: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },
        },

        "traffic": 0.7,
        "weight": 5,
        "min_length": 15,
        "max_length": 40,
    },
}