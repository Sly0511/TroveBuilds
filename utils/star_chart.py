# import re
import json
from enum import Enum
from pydantic import BaseModel, Field
from math import radians, sin, cos
from json import dumps
from copy import deepcopy

__all__ = ["StarChart", "Constellation", "Star", "StarType", "get_star_chart"]

# This code is solely used to import from .loc file into a json file
# There's no need to run this, I'll just keep updating json from here on
# However I am also not interested in losing this code bit, it may be useful

# regex = re.compile(
#     r'- id: \$gl\.([a-z]*)\.(?:([a-z0-9.*]*)\.)name\n  destination: "?(.*?)"?\n.*?\n.*?\n.*?\n.*?  destination: "?(.*?)"?$.*?\n.*?\n.*?\n(?:.*?\.details\n  destination: "?(.*?)"?\n.*?\n.*?\n)?',
#     re.MULTILINE,
# )
#
# with open(r"C:\Users\raycu\Downloads\prefabs_progression_nodes.loc") as data:
#     nodes = regex.findall(data.read())
#     star_chart = {}
#     try:
#         for tree, index, name, description, details in nodes:
#             tree = tree.capitalize()
#             if tree not in star_chart:
#                 star_chart[tree] = {"Constellation": tree, "Stars": []}
#             tree_branch = star_chart[tree]
#             indexes = (
#                 index.replace("a", "0").replace("b", "1").replace("c", "2").split(".")
#             )
#             if len(indexes) > 1:
#                 for x in indexes[:-1]:
#                     tree_branch = tree_branch["Stars"][int(x)]
#             Type = name.split(" of ")
#             Star = {
#                 "Path": tree.lower() + "." + index,
#                 "Constellation": tree,
#                 "Type": "Minor" if Type[0].startswith("Minor") else "Major",
#                 "Name": Type[1].replace("the ", " "),
#                 "Description": description,
#                 "Stats": [],
#                 "Abilities": [],
#                 "Stars": []
#             }
#             Star["Stats" if not Star["Type"] == "Major" else "Abilities"].extend(
#                 details.split("\\n")
#             )
#             tree_branch["Stars"].append(Star)
#     except IndexError:
#         print(index)
#         print("Errored Index")
#     with open("star_chart_output.json", "w+") as f:
#         f.write(json.dumps(star_chart, indent=4, separators=(",", ":")))


class StarChart(BaseModel):
    constellations: list = Field(default_factory=list)
    max_nodes: int = 40

    def __str__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"

    def __repr__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"

    def get_stars(self):
        for constellation in self.constellations:
            yield constellation
            for star in self.__iterate_stars(constellation):
                yield star

    def __iterate_stars(self, parent):
        for star in parent.children:
            yield star
            for child in self.__iterate_stars(star):
                yield child

    @property
    def activated_stars(self):
        return [
            star
            for star in self.get_stars()
            if star.unlocked and star.type != StarType.root
        ]

    @property
    def activated_stars_count(self):
        return len(self.activated_stars)

    @property
    def activated_stats(self):
        stats = {}
        percentage_stats = [
            "Attack Speed",
            "Maximum Health %",
            "Outgoing Damage",
            "Critical Hit",
            "Critical Damage",
            "Incoming Damage",
            "Damage Reduction",
            "Random Flask Emblem"
        ]
        for star in self.activated_stars:
            for stat in star.stats:
                if stat["percentage"]:
                    stat_name = stat["name"] + " Bonus"
                else:
                    stat_name = stat["name"]
                if not stats.get(stat_name):
                    stats[stat_name] = [0, (stat_name in percentage_stats or stat_name.endswith("Bonus"))]
                if stat["value"]:
                    stats[stat_name][0] += stat["value"]
                else:
                    stats[stat_name][0] = "Unknown"
        return stats

    @property
    def activated_obtainables(self):
        obtained = {}
        for star in self.activated_stars:
            for obtainable in star.obtainables:
                if not obtained.get(obtainable):
                    obtained[obtainable] = 0
                obtained[obtainable] += 1
        return obtained

    @property
    def activated_abilities(self):
        abilities = {}
        for star in self.activated_stars:
            abilities[star.path] = star.abilities
        for star in self.activated_stars:
            for ow in star.ability_overwrites:
                if ow in abilities:
                    del abilities[ow]
        return [a for ab_set in abilities.values() for a in ab_set]

class Constellation(Enum):
    combat = "Combat"
    gathering = "Gathering"
    pve = "Pve"


class ConstellationSmallColor(Enum):
    combat = "#FF8F00"
    gathering = "#00695C"
    pve = "#6A1B9A"


class ConstellationBigColor(Enum):
    combat = "#D84315"
    gathering = "#558B2F"
    pve = "#283593"


class ConstellationDisabledSmallColor(Enum):
    combat = "#aaaaaa"
    gathering = "#aaaaaa"
    pve = "#aaaaaa"


class ConstellationDisabledBigColor(Enum):
    combat = "#aaaaaa"
    gathering = "#aaaaaa"
    pve = "#aaaaaa"


class StarType(Enum):
    root = "Root"
    minor = "Minor"
    major = "Major"


class Star(BaseModel):
    constellation: Constellation
    coords: list[int]
    type: StarType
    acts: StarType
    name: str
    description: str
    stats: list[dict] = []
    abilities: list[str] = []
    unlocked: bool = False
    parent: object = None
    path: str
    children: list = []
    angle: list = []
    obtainables: list[str] = []
    ability_overwrites: list[str] = []

    def __str__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

    def __repr__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

    @property
    def color(self):
        color = (
            ConstellationBigColor[self.constellation.name].value
            if self.unlocked else
            ConstellationDisabledBigColor[self.constellation.name].value
        )
        return color

    @property
    def full_name(self):
        return self.type.value + " star of " + self.name.strip()

    @property
    def format_stats(self):
        stats = {}
        percentage_stats = [
            "Attack Speed",
            "Maximum Health %",
            "Outgoing Damage",
            "Critical Hit",
            "Critical Damage",
            "Incoming Damage",
            "Damage Reduction",
            "Random Flask Emblem"
        ]
        for stat in self.stats:
            if stat["percentage"]:
                stat_name = stat["name"] + " Bonus"
            else:
                stat_name = stat["name"]
            if not stats.get(stat_name):
                stats[stat_name] = [0, (stat_name in percentage_stats or stat_name.endswith("Bonus"))]
            if stat["value"]:
                stats[stat_name][0] += stat["value"]
            else:
                stats[stat_name][0] = "Unknown"
        return stats

    def unlock(self):
        self.unlocked = True
        if self.parent is not None:
            self.parent.unlock()

    def lock(self):
        if self.type != StarType.root:
            self.unlocked = False
        for child in self.children:
            child.lock()

    def switch_lock(self):
        if self.unlocked:
            self.lock()
        else:
            self.unlock()

    def stage_lock(self, star_chart: StarChart):
        star_chart = deepcopy(star_chart)
        star = None
        for star in star_chart.get_stars():
            if self.path == star.path:
                break
        star.switch_lock()
        return star_chart.activated_stars_count - star_chart.max_nodes

    def add_child(self, star):
        self.children.append(star)

    def add_stats(self, stats: list[str]):
        self.stats.extend(stats)

    def add_abilities(self, abilities: list[str]):
        self.stats.extend(abilities)


def build_star_chart(star_dict: dict, parent: Star = None):
    star = Star(
        path=star_dict["Path"],
        coords=star_dict["Coords"],
        constellation=Constellation(star_dict["Constellation"]),
        type=StarType(star_dict["Type"]),
        acts=StarType(star_dict["Acts"]),
        name=star_dict["Name"],
        description=star_dict["Description"],
        stats=star_dict.get("Stats", []),
        abilities=star_dict.get("Abilities", []),
        children=[],
        parent=parent,
        angle=star_dict.get("Connect", []),
        unlocked=StarType(star_dict["Type"]) == StarType.root,
        obtainables=star_dict["Obtainables"],
        ability_overwrites=star_dict.get("Overwrites", [])
    )
    for cstar in star_dict["Stars"]:
        star.add_child(build_star_chart(cstar, star))
    return star


def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    qy = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)
    return qx, qy


def build_branch(back_rotate, last_position, distance, stars):
    total_angle = 180
    splits = len(stars) + 1
    division = total_angle / splits
    for i, child in enumerate(stars, 1):
        child_rotation = division * i
        child_position = last_position[0] - distance, last_position[1]
        final_rotation = child_rotation + back_rotate
        rotated_position = rotate(
            last_position, child_position, radians(final_rotation)
        )
        child["Coords"] = rotated_position
        child["Rotation"] = final_rotation
        build_branch(
            -(90 - final_rotation),
            rotated_position,
            distance,
            child["Stars"]
        )


def rotate_branch(star, origin, angle, distance):
    for child in star["Stars"]:
        child["Coords"] = rotate(origin, child.get("Coords", [0, 0]), angle)
        connect_position_1 = (
            star["Coords"][0] - (8 if star["Type"] == "Minor" else 13),
            star["Coords"][1],
        )
        connect_position_2 = (
            child["Coords"][0] - (8 if child["Type"] == "Minor" else 13),
            child["Coords"][1],
        )
        connect_position_1 = rotate(
            star["Coords"],
            connect_position_1,
            radians(225),
        )
        connect_position_2 = rotate(child["Coords"], connect_position_2, radians(225))
        child["Connect"] = [
            connect_position_1,
            connect_position_2,
        ]
        rotate_branch(child, origin, angle, distance)
        del child["Rotation"]


def get_star_chart():
    star_chart = json.load(open("data/star_chart.json"))
    obj_star_chart = StarChart()
    origin = 320, 350
    point_distance = 55
    constell_backs = [14, 12, 4]
    for i, (constellation, back_rotate) in enumerate(
        zip(Constellation, constell_backs)
    ):
        total_angle = 360
        division = total_angle / len(Constellation)
        branch_rotation = division * i
        position = origin[0], origin[1] - point_distance
        rotated_position = rotate(origin, position, radians(branch_rotation))
        constell = star_chart[constellation.value]
        constell["Coords"] = rotated_position
        distance = 43
        build_branch(
            back_rotate, position, distance, constell["Stars"]
        )
        rotate_branch(constell, origin, radians(branch_rotation), distance)

    for constellation, data in star_chart.items():
        obj_star_chart.constellations.append(build_star_chart(data))

    return obj_star_chart
