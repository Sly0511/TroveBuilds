def radiant_level_increments(_: str, level: int):
    match level:
        case 1 | 5 | 10 | 15:
            return 0
        case 2 | 3 | 4 | 6 | 7 | 8 | 9 | 11 | 12 | 13 | 14:
            return 3
        case 16 | 17 | 18 | 19 | 21 | 22 | 23:
            return 6
        case 20:
            return 15
        case _:
            return 0


def stellar_level_increments(_: str, level: int):
    match level:
        case 1 | 5 | 10 | 15:
            return 0
        case 2 | 3 | 4 | 6 | 7 | 8 | 9 | 11 | 12 | 13 | 14:
            return 5
        case 16 | 17 | 18 | 19 | 21 | 22 | 23 | 24:
            return 10
        case 20 | 25:
            return 25
        case _:
            return 0


def crystal_level_increments(stat: str, level: int):
    pr = 7
    if stat == "Light":
        pr = 5
    match level:
        case 1 | 5 | 10 | 15:
            return 0
        case 2 | 3 | 4 | 6 | 7 | 8 | 9 | 11 | 12 | 13 | 14:
            return pr * 1
        case 16 | 17 | 18 | 19 | 21 | 22 | 23 | 24 | 26 | 27 | 28 | 29:
            return pr * 2
        case 20 | 25 | 30:
            return pr * 5
        case _:
            return 0


max_levels = {"radiant": 23, "stellar": 25, "crystal": 30}


gem_min_max = {
    "radiant": {
        "Physical Damage": {"lesser": [85, 113], "empowered": [113, 150]},
        "Magic Damage": {"lesser": [85, 113], "empowered": [113, 150]},
        "Critical Damage": {"lesser": [85, 113], "empowered": [113, 150]},
        "Critical Hit": {"lesser": [85, 113], "empowered": [113, 150]},
        "Maximum Health %": {"lesser": [85, 113], "empowered": [113, 150]},
        "Maximum Health": {"lesser": [85, 113], "empowered": [113, 150]},
        "Light": {"lesser": [85, 113], "empowered": [113, 150]},
    },
    "stellar": {
        "Physical Damage": {"lesser": [150, 200], "empowered": [200, 266]},
        "Magic Damage": {"lesser": [150, 200], "empowered": [200, 266]},
        "Critical Damage": {"lesser": [150, 200], "empowered": [200, 266]},
        "Critical Hit": {"lesser": [150, 200], "empowered": [200, 266]},
        "Maximum Health %": {"lesser": [150, 200], "empowered": [200, 266]},
        "Maximum Health": {"lesser": [150, 200], "empowered": [200, 266]},
        "Light": {"lesser": [150, 200], "empowered": [200, 266]},
    },
    "crystal": {
        "Physical Damage": {"lesser": [210, 280], "empowered": [245, 350]},
        "Magic Damage": {"lesser": [210, 280], "empowered": [245, 350]},
        "Critical Damage": {
            "lesser": [560 / 3, 770 / 3],
            "empowered": [700 / 3, 910 / 3],
        },
        "Critical Hit": {"lesser": [560 / 3, 770 / 3], "empowered": [700 / 3, 910 / 3]},
        "Maximum Health %": {"lesser": [245, 315], "empowered": [315, 385]},
        "Maximum Health": {"lesser": [245, 315], "empowered": [315, 385]},
        "Light": {"lesser": [200, 275], "empowered": [250, 300]},
    },
}


stat_multipliers = {
    "radiant": {
        "Physical Damage": [14, 14],
        "Magic Damage": [14, 14],
        "Critical Damage": [0.2, 0.2],
        "Critical Hit": [0.02, 0.02],
        "Maximum Health %": [0.5, 0.5],
        "Maximum Health": [50, 50],
        "Light": [1, 1],
    },
    "stellar": {
        "Physical Damage": [14, 14],
        "Magic Damage": [14, 14],
        "Critical Damage": [0.2, 0.2],
        "Critical Hit": [0.02, 0.02],
        "Maximum Health %": [0.5, 0.5],
        "Maximum Health": [50, 50],
        "Light": [1, 1],
    },
    "crystal": {
        "Physical Damage": [16, 16],
        "Magic Damage": [16, 16],
        "Critical Damage": [3 / 14, 3 / 14],
        "Critical Hit": [0.3 / 14, 0.3 / 14],
        "Maximum Health %": [0.5, 0.5],
        "Maximum Health": [50, 50],
        "Light": [1, 1],
    },
}


level_increments = {
    "radiant": radiant_level_increments,
    "stellar": stellar_level_increments,
    "crystal": crystal_level_increments,
}


def get_stat_values(
    gem_tier: str, gem_type: str, stat: str, level: int, boosts: int = 0
):
    min_val, max_val = stat_multipliers[gem_tier][stat]
    min_inc, max_inc = gem_min_max[gem_tier][stat][gem_type]
    # Get initial stats
    stat_output = [0, 0]
    stat_output[0] = min_inc * min_val
    stat_output[1] = max_inc * max_val
    # Calculate level stats
    for l, _ in enumerate(range(level), 1):
        level_increment = level_increments[gem_tier](stat, l)
        stat_output[0] += level_increment * min_val
        stat_output[1] += level_increment * max_val
    # Calculate boosts
    for boost in range(boosts):
        stat_output[0] += min_inc * min_val
        stat_output[1] += max_inc * max_val
    min_stat = round(stat_output[0], 2)
    max_stat = round(stat_output[1], 2)
    return min_stat, max_stat, round(max_stat - min_stat, 2)
