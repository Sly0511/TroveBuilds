# import re
import json
from enum import Enum
from pydantic import BaseModel, Field
from math import radians, sin, cos
from json import dumps

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

    def __str__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"

    def __repr__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"


class Constellation(Enum):
    combat = "Combat"
    gathering = "Gathering"
    pve = "Pve"


class ConstellationSmallColor(Enum):
    combat = "#ff6600"
    gathering = "#66ff99"
    pve = "#33ccff"


class ConstellationBigColor(Enum):
    combat = "red"
    gathering = "green"
    pve = "blue"


class StarType(Enum):
    root = "Root"
    minor = "Minor"
    major = "Major"


class Star(BaseModel):
    constellation: Constellation
    coords: list[int]
    type: StarType
    name: str
    description: str
    stats: list[str] = []
    abilities: list[str] = []
    unlocked: bool = False
    parent: object = None
    path: str
    children: list = []
    color: str = "yellow"

    def __str__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

    def __repr__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

    @property
    def full_name(self):
        return self.type.value + " star of " + self.name.strip()

    def unlock(self):
        self.unlocked = True
        if self.parent is not None:
            self.parent.unlock()

    def lock(self):
        self.unlocked = False
        for child in self.children:
            child.lock()

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
        name=star_dict["Name"],
        description=star_dict["Description"],
        stats=star_dict.get("Stats", []),
        abilities=star_dict.get("Abilities", []),
        children=[],
        parent=parent,
        color=(
            ConstellationSmallColor[star_dict["Constellation"].lower()].value
            if StarType(star_dict["Type"]) == StarType.minor else
            ConstellationBigColor[star_dict["Constellation"].lower()].value
        )
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
        rotated_position = rotate(last_position, child_position, radians(final_rotation))
        child["Coords"] = rotated_position
        build_branch(
            -(90 - final_rotation), rotated_position, distance, child["Stars"]
        )


def rotate_branch(star, origin, angle):
    for child in star["Stars"]:
        child["Coords"] = rotate(origin, child.get("Coords", [0, 0]), angle)
        rotate_branch(child, origin, angle)


def get_star_chart():
    star_chart = json.load(open("data/star_chart.json"))
    obj_star_chart = StarChart()
    origin = 600, 480
    point_distance = 120
    constell_backs = [14, 12, 4]
    for i, (constellation, back_rotate) in enumerate(zip(Constellation, constell_backs)):
        total_angle = 360
        division = total_angle / len(Constellation)
        branch_rotation = division * i
        position = origin[0], origin[1] - point_distance
        rotated_position = rotate(origin, position, radians(branch_rotation))
        constell = star_chart[constellation.value]
        constell["Coords"] = rotated_position
        build_branch(back_rotate, position, 50, constell["Stars"])
        rotate_branch(constell, origin, radians(branch_rotation))

    for constellation, data in star_chart.items():
        obj_star_chart.constellations.append(build_star_chart(data))

    return obj_star_chart
