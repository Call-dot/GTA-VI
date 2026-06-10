ROAD_TYPES = {
    "thoroughfare": {
        "layout": "_C.:./.:.C_",

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

        "entrances": (
            ("0000003-.:./.|.-4000000", "SC#-#-#-#CS", "_C.:./.|.C_",),
        ),

        "exits": (
            ("_C.:./.:.C_", "_C.:./.:.C_", "_C.:./.:.C_", "SC#-#-#-#CS", "9999991-.|./.:.-2999999",),
        ),

        "traffic": 1.0,
        "weight": 30,
        "min_length": 20,
        "max_length": 20,
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

        "entrances": (
            ("0000003-./.:.-4000000", "SC#-#-#CS", "SC./.:.CS",),
        ),

        "exits": (
            ("SC.:./.CS", "SC.:./.CS", "SC.:./.CS", "SC#-#-#CS", "9999991-.:./.-2999999",),
        ),

        "traffic": 0.7,
        "weight": 20,
        "min_length": 15,
        "max_length": 20,
        "bounds": (2, 3, 4, 5, 6)
    },

    "country": {
        "layout": "-.;.-",

        "lanes": {
            1: {
                "dir": "down",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },

            3: {
                "dir": "up",
                "type": "driving",
                "allow_spawn": True,
                "allow_overtake": True,
            },
        },

        "entrances": (
            ("d-.;.-f", "|.;.|",),
        ),

        "exits": (
            ("|.;.|", "a-.;.-s",),
        ),

        "traffic": 1.0,
        "weight": 10,
        "min_length": 20,
        "max_length": 30,
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

        "entrances": (
            ("d-.:./.|.:.-f", "SC#-#-#-#-#CS", "C.:./.:.:.C", "C.:./.:.:.C", "C.:./.:.:.C",),
        ),

        "exits": (
            ("C.:.|./.:.C", "C.:.|./.:.C", "C.:.:./.:.C", "SC#-#-#-#-#CS", "a-.:.:./.:.-s",),
        ),

        "traffic": 3.0,
        "weight": 11,
        "min_length": 10,
        "max_length": 10,
        "bounds": (1, 2, 3, 4, 5, 6, 7, 8, 9)
    },
}