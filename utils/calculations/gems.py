def radiant_level_increments(level: int):
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


def stellar_level_increments(level: int):
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


def crystal_level_increments(level: int):
    match level:
        case 1 | 5 | 10 | 15:
            return 0
        case 2 | 3 | 4 | 6 | 7 | 8 | 9 | 11 | 12 | 13 | 14:
            return 8
        case 16 | 17 | 18 | 19 | 21 | 22 | 23 | 24:
            return 10
        case 26 | 27 | 28 | 29:
            return 15
        case 20 | 25 | 30:
            return 25
        case _:
            return 0


max_levels = {"radiant": 23, "stellar": 25}


gem_min_max = {
    "radiant": {"lesser": [85, 113], "empowered": [113, 150]},
    "stellar": {"lesser": [150, 200], "empowered": [200, 266]},
    "crystal": {"lesser": [240, 320], "empowered": [200, 266]},
}


stat_multipliers = {
    "Physical Damage": [14, 14],
    "Magic Damage": [14, 14],
    "Critical Damage": [0.2, 0.2],
    "Critical Hit": [0.02, 0.02],
    "Maximum Health %": [0.5, 0.5],
    "Maximum Health": [50, 50],
    "Light": [1, 1],
}


level_increments = {
    "radiant": radiant_level_increments,
    "stellar": stellar_level_increments,
    "crystal": crystal_level_increments,
}


def get_stat_values(
    gem_tier: str, gem_type: str, stat: str, level: int, boosts: int = 0
):
    min_val, max_val = stat_multipliers[stat]
    min_inc, max_inc = gem_min_max[gem_tier][gem_type]
    # Get initial stats
    stat_output = [0, 0]
    stat_output[0] = min_inc * min_val
    stat_output[1] = max_inc * max_val
    # Calculate level stats
    for l, _ in enumerate(range(level), 1):
        level_increment = level_increments[gem_tier](l)
        stat_output[0] += level_increment * min_val
        stat_output[1] += level_increment * max_val
    # Calculate boosts
    for boost in range(boosts):
        stat_output[0] += min_inc * min_val
        stat_output[1] += max_inc * max_val
    min_stat = round(stat_output[0], 2)
    max_stat = round(stat_output[1], 2)
    return min_stat, max_stat, round(max_stat - min_stat, 2)
