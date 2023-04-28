import itertools
from json import load

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
    Switch,
    Slider,
    VerticalDivider,
    Container,
    TextField,
    IconButton,
    ElevatedButton,
    Icon,
)
from flet.security import encrypt, decrypt
from flet_core.icons import COPY, CALCULATE

from models.objects import Controller
from models.objects.builds import (
    TroveClass,
    Class,
    StatName,
    BuildConfig,
    BuildType,
    DamageType,
    AbilityType,
)
from utils.functions import get_attr, throttle, chunks


class GemBuildsController(Controller):
    def setup_controls(self):
        if not hasattr(self, "classes"):
            self.selected_build = None
            self.build_page = 0
            self.max_pages = 0
            self.classes = {}
            for trove_class in load(open("data/classes.json")):
                self.classes[trove_class["name"]] = TroveClass(**trove_class)
            self.foods = load(open("data/builds/food.json"))
            self.allies = load(open("data/builds/ally.json"))
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
                                            disabled=c.name
                                            == self.config.character.name,
                                        )
                                        for c in Class
                                        if not self.config.subclass
                                        or (
                                            self.config.subclass
                                            and c.name != self.config.subclass.name
                                        )
                                    ],
                                    on_change=self.set_class,
                                ),
                                Dropdown(
                                    label="Subclass",
                                    value=self.selected_subclass.name.name,
                                    options=[
                                        dropdown.Option(
                                            key=c.name,
                                            text=c.value,
                                            disabled=c.name
                                            == self.config.subclass.name,
                                        )
                                        for c in Class
                                        if c.name != self.config.character.name
                                    ],
                                    on_change=self.set_subclass,
                                ),
                                Dropdown(
                                    label="Build Type",
                                    value=self.config.build_type.name,
                                    options=[
                                        dropdown.Option(
                                            key=b.name,
                                            text=b.value,
                                            disabled=b.name
                                            == self.config.build_type.name,
                                        )
                                        for b in BuildType
                                        if b != BuildType.health
                                    ],
                                    on_change=self.set_build_type,
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
                        Dropdown(
                            label="Ally",
                            value=self.config.ally,
                            options=[
                                dropdown.Option(
                                    key=name,
                                    text=name,
                                    disabled=name == self.config.ally,
                                )
                                for name in self.allies.keys()
                            ],
                            on_change=self.set_ally,
                        ),
                        Text("Stats", size=20),
                        *[
                            Text(
                                str(round(s["value"], 2))
                                + ("% " if s["percentage"] else " ")
                                + s["name"]
                            )
                            for s in self.allies[self.config.ally]["stats"]
                        ],
                        Text("Abilities", size=20),
                        *[Text(a) for a in self.allies[self.config.ally]["abilities"]],
                    ]
                ),
                col=3,
            ),
            Card(
                content=Column(
                    controls=[
                        Dropdown(
                            label="Food",
                            value=self.config.food,
                            options=[
                                dropdown.Option(
                                    key=name,
                                    text=name,
                                    disabled=name == self.config.food,
                                )
                                for name in self.foods.keys()
                            ],
                            on_change=self.set_food,
                        ),
                        Column(
                            controls=[
                                Text(
                                    f"Critical Damage stats on gear: {self.config.critical_damage_count}"
                                ),
                                Slider(
                                    min=0,
                                    max=3,
                                    divisions=3,
                                    value=self.config.critical_damage_count,
                                    label="{value}",
                                    on_change_end=self.set_cd_count,
                                ),
                            ]
                        ),
                        Row(
                            controls=[
                                Column(
                                    controls=[
                                        Text("Damage on face"),
                                        Switch(
                                            value=not self.config.no_face,
                                            on_change=self.toggle_face,
                                        ),
                                    ]
                                ),
                                VerticalDivider(),
                                Column(
                                    controls=[
                                        Text("Subclass ability active"),
                                        Switch(
                                            value=self.config.subclass_active,
                                            on_change=self.toggle_subclass_active,
                                        ),
                                    ]
                                ),
                                VerticalDivider(),
                                Column(
                                    controls=[
                                        Text("Berserker Battler"),
                                        Switch(
                                            value=self.config.berserker_battler,
                                            on_change=self.toggle_berserker_battler,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    spacing=11,
                ),
                col=3,
            ),
            Card(
                content=Column(
                    controls=[
                        # Column(
                        #     controls=[
                        #         Text("Crystal 5 (WIP)"),
                        #         Switch(
                        #             label="",
                        #             value=self.config.crystal_5,
                        #             on_change=self.toggle_crystal_5,
                        #             disabled=True
                        #         )
                        #     ]
                        # ),
                        Switch(
                            label="Star Chart",
                            value=self.config.star_chart,
                            on_change=self.toggle_star_chart,
                        ),
                        Text("250 Light\n27% Bonus Damage\n35% Critical Damage")
                        if self.config.star_chart
                        else Text(),
                        *[
                            TextField(
                                label="Light",
                                value=str(self.config.light),
                                on_submit=self.set_light,
                            )
                            for _ in range(1)
                            if self.config.build_type != BuildType.light
                        ],
                        Text("Predictions", size=22),
                        Column(
                            controls=[
                                Text("Cosmic Primordial"),
                                Switch(
                                    value=self.config.cosmic_primordial,
                                    on_change=self.toggle_cosmic_primordial,
                                ),
                            ]
                        ),
                    ],
                    spacing=11,
                ),
                col=2,
            ),
        ]
        if not hasattr(self, "features"):
            self.features = Row()
        self.features.controls.clear()
        self.features.controls.extend(
            [
                VerticalDivider(),
                ElevatedButton("First", data=0, on_click=self.change_build_page),
                # ElevatedButton(
                #     "Backward 5",
                #     data=self.build_page - 5,
                #     on_click=self.change_build_page,
                # ),
                ElevatedButton(
                    "Previous",
                    data=self.build_page - 1,
                    on_click=self.change_build_page,
                ),
                ElevatedButton(
                    "Next page",
                    data=self.build_page + 1,
                    on_click=self.change_build_page,
                ),
                # ElevatedButton(
                #     "Forward 5",
                #     data=self.build_page + 5,
                #     on_click=self.change_build_page,
                # ),
                ElevatedButton(
                    "Last", data=self.max_pages - 1, on_click=self.change_build_page
                ),
                VerticalDivider(),
                TextField(
                    data=encrypt(self.config.to_base_64(), self.page.secret_key),
                    label="Insert build string",
                    on_submit=self.set_build_string,
                ),
                Container(
                    content=Row(controls=[Icon(COPY), Text("Copy build string")]),
                    on_click=self.copy_build_string,
                    on_hover=self.copy_build_hover,
                    padding=15,
                    border_radius=10,
                ),
            ]
        )
        if not hasattr(self, "data_table"):
            self.coeff_table = DataTable(
                columns=[
                    DataColumn(label=Text("Rank")),
                    DataColumn(label=Text("Build")),
                    DataColumn(label=Text("Light")),
                    DataColumn(label=Text("Base Damage")),
                    DataColumn(label=Text("Bonus Damage")),
                    DataColumn(label=Text("Damage")),
                    DataColumn(label=Text("Critical")),
                    DataColumn(label=Text("Coefficient")),
                    DataColumn(label=Text("Deviation")),
                    DataColumn(label=Text("Is Cheap?")),
                    DataColumn(label=Text("")),
                ],
                bgcolor="#212223",
                col=8,
            )
            self.abilities = DataTable(
                columns=[
                    DataColumn(Text("")),
                    DataColumn(Text("")),
                    DataColumn(
                        Row(
                            [
                                Text("", width=70, size=10),
                                Text(
                                    "Critical", width=70, size=10, text_align="center"
                                ),
                                Text(
                                    "Emblem 2.5x",
                                    width=70,
                                    size=10,
                                    text_align="center",
                                ),
                            ]
                        )
                    ),
                ],
                heading_row_height=15,
                data_row_height=80,
            )
            self.abilities_table = Card(
                content=Column(
                    controls=[Text("Abilities", size=22), self.abilities],
                    horizontal_alignment="center",
                ),
                col=4,
            )
            self.data_table = Container(
                content=ResponsiveRow(controls=[self.coeff_table, self.abilities_table])
            )
        self.abilities_table.visible = bool(self.selected_build)
        if self.config.character:
            self.coeff_table.rows.clear()
            builds = self.calculate_results()
            builds.sort(key=lambda x: [abs(x[4] - self.config.light), -x[6]])
            builds = [[i] + b for i, b in enumerate(builds, 1)]
            if self.selected_build is None:
                self.selected_build = builds[0]
            paged_builds = chunks(builds, 10)
            self.max_pages = len(paged_builds)
            if self.build_page < 0:
                self.build_page = self.max_pages - 1
            elif self.build_page > self.max_pages - 1:
                self.build_page = 0
            top = 0
            for (
                rank,
                build,
                first,
                second,
                third,
                fourth,
                final,
                coefficient,
            ) in paged_builds[self.build_page]:
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
                if (
                    3 <= build[0][0] <= 6
                    and 3 <= build[0][1] <= 6
                    and 6 <= build[1][0] <= 12
                    and 6 <= build[1][1] <= 12
                ):
                    cheap = True
                else:
                    cheap = False
                build_data = [
                    build,
                    first,
                    second,
                    third,
                    fourth,
                    final,
                    coefficient,
                ]
                self.coeff_table.rows.append(
                    DataRow(
                        cells=[
                            DataCell(content=Text(f"{rank}")),
                            DataCell(
                                content=Text(f"{build_text}"),
                                on_tap=self.copy_to_clipboard,
                            ),
                            DataCell(content=Text(f"{third:,}")),
                            DataCell(content=Text(f"{round(first, 2):,}")),
                            DataCell(content=Text(f"{round(fourth, 2):,}%")),
                            DataCell(content=Text(f"{round(final, 2):,}")),
                            DataCell(content=Text(f"{round(second, 2):,}%")),
                            DataCell(
                                content=Text(f"{coefficient:,}"),
                                on_tap=self.copy_to_clipboard,
                            ),
                            DataCell(
                                content=Text(
                                    f"{round(abs(coefficient - top) / top * 100, 3)}%"
                                    if top
                                    else "Best"
                                )
                            ),
                            DataCell(
                                content=Container(
                                    bgcolor="#a00000" if cheap else "#a00000"
                                )
                            ),
                            DataCell(
                                content=Row(
                                    controls=[
                                        IconButton(
                                            COPY,
                                            data=self.get_build_string(
                                                [
                                                    build_text,
                                                    first,
                                                    second,
                                                    third,
                                                    fourth,
                                                    final,
                                                    coefficient,
                                                ]
                                            ),
                                            on_click=self.copy_build_clipboard,
                                        ),
                                        IconButton(
                                            CALCULATE,
                                            data=build_data,
                                            on_click=self.select_build,
                                        ),
                                    ]
                                )
                            ),
                        ],
                        color="#156b16"
                        if build_data == self.selected_build
                        else ("#313233" if rank % 2 else "#414243"),
                    )
                )
                if not top:
                    top = coefficient
        self.abilities.rows.clear()
        self.abilities.visible = bool(self.selected_build)
        self.abilities.rows.extend(
            [
                *[
                    DataRow(
                        cells=[
                            DataCell(
                                content=Stack(
                                    controls=[
                                        Image(a.icon_path, top=6, left=5),
                                        *[
                                            Image(
                                                "assets/images/abilities/gem_frame.png"
                                            )
                                            for i in range(1)
                                            if a.type == AbilityType.upgrade
                                        ],
                                    ],
                                )
                            ),
                            DataCell(content=Text(a.name)),
                            DataCell(
                                content=Column(
                                    controls=[
                                        Row(
                                            controls=[
                                                Text(s.name, size=10, width=70),
                                                Text(
                                                    f"{round(s.base + s.multiplier * self.selected_build[6]):,}",
                                                    size=10,
                                                    width=70,
                                                    text_align="center",
                                                ),
                                                Text(
                                                    f"{round(s.base + s.multiplier * self.selected_build[6]*2.5):,}",
                                                    size=10,
                                                    width=70,
                                                    text_align="center",
                                                ),
                                            ],
                                        )
                                        for s in a.stages
                                    ],
                                    alignment="center",
                                    spacing=1,
                                )
                            ),
                        ]
                    )
                    for a in self.selected_class.abilities
                ]
            ]
        )

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
        first += self.sum_file_values(f"dragons_damage")
        second += self.sum_file_values("dragons_critical_damage")
        # Food stats
        food = self.foods[self.config.food]
        for stat in food["stats"]:
            if stat["name"] == damage_type.value:
                if stat["percentage"]:
                    fourth += stat["value"]
                else:
                    first += stat["value"]
            if stat["name"] == StatName.critical_damage.value:
                second += stat["value"]
            if stat["name"] == StatName.light.value:
                third += stat["value"]
        # Ally stats
        ally = self.allies[self.config.ally]
        for stat in ally["stats"]:
            if stat["name"] == damage_type.value:
                if stat["percentage"]:
                    fourth += stat["value"]
                else:
                    first += stat["value"]
            if stat["name"] == StatName.critical_damage.value:
                second += stat["value"]
            if stat["name"] == StatName.light.value:
                third += stat["value"]
        # Add Star Chart stats
        if self.config.star_chart:
            second += 35
            third += 250
            fourth += 27
        # Remove critical damage stats from equipments (movement speed builds)
        second -= 44.2 * (3 - self.config.critical_damage_count)
        # Solarion 140 Light
        if Class.solarion in [self.config.character, self.config.subclass]:
            third += 140
        # Lunar Lancer subclass
        if damage_type == StatName.physical_damage:
            if self.config.subclass in [Class.lunar_lancer]:
                first += 750
        # Shadow Hunter and Ice Sage
        if damage_type == StatName.magic_damage:
            if self.config.subclass in [Class.ice_sage, Class.shadow_hunter]:
                first += 750
        # Bard and Boomeranger subclasses
        if self.config.subclass in [Class.bard, Class.boomeranger]:
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
        # Berserker battler stats
        if self.config.berserker_battler:
            third += 750
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
            if self.config.build_type not in [BuildType.health]:
                if class_bonus := get_attr(
                    self.selected_class.bonuses, name=damage_type.value
                ):
                    cfirst *= 1 + (class_bonus / 100)
                final = cfirst * (1 + fourth / 100)
            else:
                final = cfirst
            coefficient = round(final * (1 + csecond / 100))
            build_stats = [
                build,
                cfirst,
                csecond,
                cthird,
                fourth,
                final,
                coefficient,
            ]
            # if build == [[5, 4], [8, 10], [0, 0, 3], [0, 0, 6]]:
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
        self.selected_build = None
        self.config.character = Class[event.control.value]
        self.selected_class = self.classes.get(self.config.character.value, None)
        damage_type = (
            StatName.magic_damage
            if self.selected_class.damage_type == DamageType.magic
            else StatName.physical_damage
        )
        if damage_type == DamageType.magic:
            self.config.ally = "Starry Skyfire"
        elif damage_type == DamageType.physical:
            self.config.ally = "Scorpius"
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

    async def set_food(self, event):
        self.config.food = event.control.value
        self.setup_controls()
        await self.page.update_async()

    async def set_ally(self, event):
        self.config.ally = event.control.value
        self.setup_controls()
        await self.page.update_async()

    async def toggle_berserker_battler(self, _):
        self.config.berserker_battler = not self.config.berserker_battler
        self.setup_controls()
        await self.page.update_async()

    async def toggle_star_chart(self, _):
        self.config.star_chart = not self.config.star_chart
        self.setup_controls()
        await self.page.update_async()

    @throttle
    async def set_light(self, event):
        event.control.border_color = None
        try:
            value = int(event.control.value)
            self.config.light = value
            self.setup_controls()
            await event.control.update_async()
        except ValueError:
            event.control.border_color = "red"
            return await event.control.update_async()

    async def change_build_page(self, event):
        self.build_page = event.control.data
        self.setup_controls()
        await self.page.update_async()

    async def set_build_string(self, event):
        try:
            self.config = BuildConfig.from_base_64(
                decrypt(event.control.value, self.page.secret_key)
            )
        except:
            ...
        self.setup_controls()
        await self.page.update_async()

    async def select_build(self, event):
        if self.selected_build == event.control.data:
            self.selected_build = None
        else:
            self.selected_build = event.control.data
        self.page.snack_bar.content.value = "Ability build changed"
        self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    async def copy_build_string(self, _):
        await self.page.set_clipboard_async(self.features.controls[0].data)
        self.page.snack_bar.content.value = "Copied to clipboard"
        self.page.snack_bar.open = True
        await self.page.update_async()

    async def copy_to_clipboard(self, event):
        if value := event.control.content.value:
            await self.page.set_clipboard_async(str(value))
            self.page.snack_bar.content.value = "Copied to clipboard"
            self.page.snack_bar.open = True
        await self.page.update_async()

    def get_build_string(self, data):
        string = ""
        string += f"Build: {data[0]}\n"
        string += f"Light: {data[2]}\n"
        string += f"Base Damage: {round(data[1], 2)}\n"
        string += f"Bonus Damage: {data[4]}\n"
        string += f"Damage: {round(data[5], 2)}\n"
        string += f"Critical Damage: {data[2]}\n"
        string += f"Coefficient: {data[6]}"
        return string

    async def copy_build_clipboard(self, event):
        await self.page.set_clipboard_async(event.control.data)
        self.page.snack_bar.content.value = "Copied to clipboard"
        self.page.snack_bar.open = True
        await self.page.update_async()

    async def copy_build_hover(self, event):
        event.control.ink = True
        await event.control.update_async()
