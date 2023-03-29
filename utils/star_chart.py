# import re
import json
from enum import Enum
from pydantic import BaseModel, Field

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
#                 "Constellation": tree,
#                 "Type": "Minor" if Type[0].startswith("Minor") else "Major",
#                 "Name": Type[1].replace("the ", " "),
#                 "Description": description,
#                 "Stats": [],
#                 "Abilities": [],
#                 "Stars": [],
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
    constellations: dict = Field(default_factory=dict)

    def __str__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"

    def __repr__(self):
        return f"<StarChart constellations=[{', '.join([c.value for c in self.constellations.keys()])}]>"


class Constellation(Enum):
    combat = "Combat"
    gathering = "Gathering"
    pve = "Pve"


class StarType(Enum):
    minor = "Minor"
    major = "Major"


class Star(BaseModel):
    constellation: Constellation
    type: StarType
    name: str
    description: str
    stats: list[str] = []
    abilities: list[str] = []
    unlocked: bool = False
    parent: object = None
    children: list = []

    def __str__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

    def __repr__(self):
        return f'<Star name="{self.name}" type={self.type.value} unlocked={self.unlocked} children={len(self.children)}>'

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
        constellation=Constellation(star_dict["Constellation"]),
        type=StarType(star_dict["Type"]),
        name=star_dict["Name"],
        description=star_dict["Description"],
        stats=star_dict["Stats"],
        abilities=star_dict["Abilities"],
        children=[],
        parent=parent,
    )
    for cstar in star_dict["Stars"]:
        star.add_child(build_star_chart(cstar, star))
    return star


def get_star_chart():
    star_chart = json.load(open("data/star_chart.json"))
    obj_star_chart = StarChart()
    for constellation in Constellation:
        obj_star_chart.constellations.update(
            {
                constellation: build_star_chart(
                    star_chart[constellation.value]["Stars"][0]
                )
            }
        )
    return obj_star_chart
