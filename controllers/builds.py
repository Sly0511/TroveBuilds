import asyncio

from flet import (
    Text,
    ResponsiveRow,
    Dropdown,
    dropdown,
    Image,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    Column,
    Card,
    Row,
    Stack,
    CircleAvatar,
    Switch,
    Slider,
    Divider
)
from json import load
import itertools


from models.objects import Controller
from models.objects.builds import (
    TroveClass,
    Class,
    StatName,
    BuildConfig,
    BuildType,
    DamageType,
)
from utils.functions import get_key, get_attr


class GemBuildsController(Controller):
    def setup_controls(self):
        if not hasattr(self, "classes"):
            self.classes = {}
            for trove_class in load(open("data/classes.json")):
                self.classes[trove_class["name"]] = TroveClass(**trove_class)
            self.config = BuildConfig()
        self.selected_class = self.classes.get(self.config.character.value, None)
        self.selected_subclass = self.classes.get(self.config.subclass.value, None)
        if not hasattr(self, "character_data"):
            self.character_data = ResponsiveRow()
        self.character_data.controls = [
            Card(
                content=Row(
                    controls=[
                        Stack(
                            controls=[
                                Image(
                                    src=self.selected_class.image_path,
                                    width=275,
                                ),
                                Image(
                                    src=self.selected_subclass.icon_path,
                                    width=75,
                                    top=150,
                                    left=170,
                                ),
                            ]
                        ),
                        Column(
                            controls=[
                                Dropdown(
                                    label="Class",
                                    value=self.selected_class.name.name,
                                    options=[
                                        dropdown.Option(
                                            key=c.name,
                                            text=c.value,
                                            disabled=c.name == self.config.character.name
                                        )
                                        for c in Class
                                        if not self.config.subclass
                                        or (
                                            self.config.subclass
                                            and c.name != self.config.subclass.name
                                        )
                                    ],
                                    on_change=self.set_class
                                ),
                                Dropdown(
                                    label="Subclass",
                                    value=self.selected_subclass.name.name,
                                    options=[
                                        dropdown.Option(
                                            key=c.name,
                                            text=c.value,
                                            disabled=c.name == self.config.subclass.name
                                        )
                                        for c in Class
                                        if c.name != self.config.character.name
                                    ],
                                    on_change=self.set_subclass
                                ),
                                Dropdown(
                                    label="Build Type",
                                    value=self.config.build_type.name,
                                    options=[
                                        dropdown.Option(
                                            key=b.name,
                                            text=b.value,
                                            disabled=b.name == self.config.build_type.name
                                        )
                                        for b in BuildType
                                    ],
                                    on_change=self.set_build_type
                                ),
                            ]
                        ),
                    ]
                ),
                col=4,
            ),
            Card(
                content=Column(
                    controls=[
                        Column(
                            controls=[
                                Text(f"Critical Damage stats on gear: {self.config.critical_damage_count}"),
                                Slider(
                                    min=0,
                                    max=3,
                                    divisions=3,
                                    value=self.config.critical_damage_count,
                                    label="{value}",
                                    on_change_end=self.set_cd_count
                                )
                            ]
                        ),
                        Column(
                            controls=[
                                Text("Damage on face"),
                                Switch(
                                    value=not self.config.no_face,
                                    on_change=self.toggle_face
                                )
                            ]
                        ),
                        Column(
                            controls=[
                                Text("Subclass ability active"),
                                Switch(
                                    label="",
                                    value=self.config.subclass_active,
                                    on_change=self.toggle_subclass_active
                                )
                            ]
                        ),
                    ],
                    spacing=11
                ),
                col=3
            ),
            Card(
                content=Column(
                    controls=[
                        Text("Predictions", size=22),
                        Column(
                            controls=[
                                Text("Cosmic Primordial"),
                                Switch(
                                    value=self.config.cosmic_primordial,
                                    on_change=self.toggle_cosmic_primordial
                                )
                            ]
                        ),
                        Column(
                            controls=[
                                Text("Crystal 5 (WIP)"),
                                Switch(
                                    label="",
                                    value=self.config.crystal_5,
                                    on_change=self.toggle_crystal_5,
                                    disabled=True
                                )
                            ]
                        ),
                    ],
                    spacing=11
                ),
                col=1
            )
        ]
        if not hasattr(self, "data_table"):
            self.data_table = DataTable(
                columns=[
                    DataColumn(label=Text("Rank")),
                    DataColumn(label=Text("Build")),
                    DataColumn(label=Text("Coefficient")),
                    DataColumn(label=Text("Light")),
                    DataColumn(label=Text("Difference #1")),
                    DataColumn(label=Text("Mod coefficient")),
                    # DataColumn(label=Text("Is Cheap?")),
                ],
            )
        if self.config.character:
            self.data_table.rows.clear()
            builds = self.calculate_results()[:10]
            builds.sort(key=lambda x: [abs(x[4] - self.config.light), -x[6]])
            top = 0
            for i, (
                build,
                first,
                second,
                third,
                fourth,
                final,
                coefficient,
                mod_coefficient,
            ) in enumerate(builds, 1):
                boosts = []
                [boosts.extend(i) for i in build]
                if not self.config.light or (
                    self.config.light and self.config.build_type in [BuildType.health]
                ):
                    del boosts[6]
                    del boosts[8]
                if not self.config.light and self.config.build_type not in [
                    BuildType.health
                ]:
                    boosts = boosts[:4]
                build_text = "/".join([str(i) for i in boosts][:4]) + (
                    " + " + "/".join([str(i) for i in boosts][4:])
                    if len(boosts) > 4
                    else ""
                )
                self.data_table.rows.append(
                    DataRow(
                        cells=[
                            DataCell(content=Text(f"{i}")),
                            DataCell(content=Text(f"{build_text}")),
                            DataCell(content=Text(f"{coefficient}")),
                            DataCell(content=Text(f"{third}")),
                            DataCell(content=Text(f"{abs(coefficient - top)}")),
                            DataCell(content=Text(f"{mod_coefficient}")),
                            # DataCell(content=Text(f"Yes")),
                        ]
                    )
                )
                if not top:
                    top = coefficient

    def setup_events(self):
        ...

    def calculate_results(self):
        if self.config.build_type in [BuildType.health]:
            return list(self.calculate_health_build_stats())
        elif self.config.build_type in [BuildType.light, BuildType.farm]:
            return list(self.calculate_damage_build_stats())

    def calculate_health_build_stats(self):
        first = 0
        second = 0
        first += self.sum_file_values("health")
        second += self.sum_file_values("health_per")
        first += get_attr(
            self.selected_class.stats, name=StatName("Maximum Health")
        ).value
        second += get_attr(
            self.selected_class.stats, name=StatName("Maximum Health %")
        ).value
        if self.selected_class.subclass in [Class.chloromancer]:
            second += 60
        if self.config.crystal_5:
            first += 17290
            second += 104
        return first, second, 0, 0

    def calculate_damage_build_stats(self):
        first = 0
        second = 0
        third = 0
        fourth = 0
        first += self.sum_file_values("damage")
        second += self.sum_file_values("critical_damage")
        third += self.sum_file_values("light")
        fourth += self.sum_file_values("bonus_damage")
        damage_type = (
            StatName.magic_damage
            if self.selected_class.damage_type == DamageType.magic
            else StatName.physical_damage
        )
        first += get_attr(self.selected_class.stats, name=damage_type).value
        second += get_attr(
            self.selected_class.stats, name=StatName("Critical Damage")
        ).value
        if not self.config.no_face:
            first += 4719
        # Dragon stats
        first += self.sum_file_values(f"{damage_type.name}/dragons_damage")
        second += self.sum_file_values("critical_damage")
        # Remove critical damage stats from equipments (movement speed builds)
        second -= 44.2 * (3 - self.config.critical_damage_count)
        # Solarion 140 Light
        if Class.solarion in [self.config.character, self.config.subclass]:
            third += 140
        # Lunar Lancer subclass
        if damage_type == StatName.physical_damage and self.config.subclass in [
            Class.lunar_lancer
        ]:
            first += 750
        # Bard and Boomeranger subclasses
        if damage_type == StatName.magic_damage and self.config.subclass in [
            Class.bard,
            Class.boomeranger,
        ]:
            second += 20
        # Active subclass boosts
        if self.config.subclass_active:
            # Bard
            if self.config.subclass in [Class.bard]:
                fourth += 45
                second += 45
            # Gunslinger
            if self.config.subclass in [Class.gunslinger]:
                fourth += 5.5
            # Lunar Lancer and Candy Barbarian
            if self.config.subclass in [Class.lunar_lancer, Class.candy_barbarian]:
                fourth += 30
        # Crystal 5 (will implement later)
        ...
        builder = self.generate_combinations(
            farm=self.config.build_type in [BuildType.farm],
            coeff=self.config.build_type in [BuildType.health],
        )
        for build_tuple in builder:
            build = list(build_tuple)
            gem_first, gem_second, gem_third = self.calculate_gem_stats(
                self.config, build
            )
            cfirst = first + gem_first
            csecond = second + gem_second
            cthird = third + gem_third
            if self.config.build_type in [BuildType.health]:
                cfirst *= 1 + (
                    get_key(self.selected_class.bonuses, {"name": damage_type.value})
                    / 100
                )
                final = cfirst * (1 + fourth / 100)
            else:
                final = cfirst
            coefficient = round(final * (1 + csecond / 100))
            mod_coefficient = int(round(final) * (1 + round(csecond, 1) / 100))
            build_stats = [
                build,
                cfirst,
                csecond,
                cthird,
                fourth,
                final,
                coefficient,
                mod_coefficient,
            ]
            yield build_stats

    def sum_file_values(self, path):
        data = load(open(f"data/builds/{path}.json"))
        return sum(data.values())

    def calculate_gem_stats(self, config: BuildConfig, build):
        first = 0
        second = 0
        third = 0
        cosmic_first = 0
        cosmic_second = 0
        if not hasattr(self, "gem_stats"):
            self.gem_stats = load(open(f"data/gems/crystal.json"))
        if config.build_type == BuildType.health:
            first_lesser = self.gem_stats["Lesser"]["Maximum Health"]
            first_empowered = self.gem_stats["Empowered"]["Maximum Health"]
            second_lesser = self.gem_stats["Lesser"]["Maximum Health %"]
            second_empowered = self.gem_stats["Empowered"]["Maximum Health %"]
        else:
            first_lesser = self.gem_stats["Lesser"]["Damage"]
            first_empowered = self.gem_stats["Empowered"]["Damage"]
            second_lesser = self.gem_stats["Lesser"]["Critical Damage"]
            second_empowered = self.gem_stats["Empowered"]["Critical Damage"]
        third_lesser = self.gem_stats["Lesser"]["Light"]
        third_empowered = self.gem_stats["Empowered"]["Light"]
        # Add base stats from gems
        first += 3 * first_empowered[0]
        first += 6 * first_lesser[0]
        second += 3 * second_empowered[0]
        second += 6 * second_lesser[0]
        third += 1 * third_empowered[0]
        third += 2 * third_lesser[0]
        cosmic_first += 1 * first_empowered[0]
        cosmic_first += 2 * first_lesser[0]
        cosmic_second += 1 * second_empowered[0]
        cosmic_second += 2 * second_lesser[0]
        # Add stats from boosts
        first += first_empowered[1] * build[0][0]
        second += second_empowered[1] * build[0][1]
        first += first_lesser[1] * build[1][0]
        second += second_lesser[1] * build[1][1]
        cosmic_first += first_empowered[1] * build[2][0]
        cosmic_second += second_empowered[1] * build[2][1]
        third += third_empowered[1] * build[2][2]
        cosmic_first += first_lesser[1] * build[3][0]
        cosmic_second += second_lesser[1] * build[3][1]
        third += third_lesser[1] * build[3][2]
        # Cosmic primordial dragon
        if self.config.cosmic_primordial:
            first = (first + cosmic_first) * 1.1
            second = (second + cosmic_second) * 1.1
            third = third * 1.1
        else:
            first = first * 1.1 + cosmic_first
            second = second * 1.1 + cosmic_second
        return first, second, third

    def generate_combinations(self, farm=False, coeff=False):
        first_set = [[i, 9 - i] for i in range(10)]
        second_set = [[i, 18 - i] for i in range(19)]
        third_set = [
            [x, y, z]
            for x in range(4)
            for y in range(4)
            for z in range(4)
            if x + y + z == 3 and (not farm or x + y == 3) and (coeff or farm or z == 3)
        ]
        fourth_set = [
            [x, y, z]
            for x in range(7)
            for y in range(7)
            for z in range(7)
            if x + y + z == 6 and (not farm or x + y == 6) and (coeff or farm or z == 6)
        ]
        return itertools.product(first_set, second_set, third_set, fourth_set)

    async def set_class(self, event):
        self.config.character = Class[event.control.value]
        self.setup_controls()
        await self.page.update_async()

    async def set_subclass(self, event):
        self.config.subclass = Class[event.control.value]
        self.setup_controls()
        await self.page.update_async()

    async def set_build_type(self, event):
        self.config.build_type = BuildType[event.control.value]
        self.setup_controls()
        await self.page.update_async()

    async def toggle_face(self, _):
        self.config.no_face = not self.config.no_face
        self.setup_controls()
        await self.page.update_async()

    async def set_cd_count(self, event):
        self.config.critical_damage_count = int(event.control.value)
        self.setup_controls()
        await self.page.update_async()

    async def toggle_subclass_active(self, _):
        self.config.subclass_active = not self.config.subclass_active
        self.setup_controls()
        await self.page.update_async()

    async def toggle_cosmic_primordial(self, _):
        self.config.cosmic_primordial = not self.config.cosmic_primordial
        self.setup_controls()
        await self.page.update_async()

    async def toggle_crystal_5(self, _):
        self.config.crystal_5 = not self.config.crystal_5
        self.setup_controls()
        await self.page.update_async()
