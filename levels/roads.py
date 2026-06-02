ROAD_TYPES = {
    "thoroughfare": {
        "layout": "__.:./.:.__",

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

            6: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            8: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },
        },

        "traffic": 1.0,
        "weight": 10,
        "min_length": 20,
        "max_length": 50,
        "bounds": (2, 3, 4, 5, 6, 7, 8)
    },

    "small_town": {
        "layout": "SC.;.;.CS",

        "lanes": {
            2: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            4: {
                "dir": "both",
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

        "traffic": 0.7,
        "weight": 50,
        "min_length": 15,
        "max_length": 40,
        "bounds": (2, 3, 4, 5, 6)
    },

    "road": {
        "layout": "__.:./.:.__",

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

            6: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            8: {
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
        "bounds": (2, 3, 4, 5, 6, 7, 8)
    },

    "stroad": {
        "layout": "C.:.;.;.:.C",

        "lanes": {
            1: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            3: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            5: {
                "dir": "both",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            7: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            9: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },
        },

        "traffic": 3.0,
        "weight": 10,
        "min_length": 20,
        "max_length": 60,
        "bounds": (1, 2, 3, 4, 5, 6, 7, 8, 9)
    },
}