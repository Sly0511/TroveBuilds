import asyncio
from random import choice

from flet import (
    ResponsiveRow,
    Column,
    Row,
    Container,
    Card,
    Image,
    Text,
    Border,
    BorderSide,
    Dropdown,
    dropdown,
    Slider,
    Switch,
    ElevatedButton
)
from i18n import t

from models.objects import Controller
from models.objects.gem import (
    LesserGem,
    EmpoweredGem,
    GemElement,
    GemTier,
    GemType,
    GemRestriction,
    Stat,
)
from utils.calculations.gems import max_levels
from utils.functions import throttle
from utils.path import BasePath


class GemsController(Controller):
    def setup_controls(self, gem=None):
        self.selected_gem = gem
        used_abilities = []
        if not hasattr(self, "gem_report"):
            self.gem_report = ResponsiveRow(controls=[Text("Gem Stat Report", size=21)])
        # Build a gem set
        if not hasattr(self, "gem_set"):
            self.gem_set = []
            for element in [
                GemElement.fire,
                GemElement.water,
                GemElement.air,
                GemElement.cosmic,
            ]:
                element_set = []
                for gem_builder in [EmpoweredGem, LesserGem, LesserGem]:
                    while gem := gem_builder.random_gem(
                        tier=GemTier.crystal, element=element
                    ):
                        if isinstance(gem, EmpoweredGem):
                            if gem.ability in used_abilities:
                                continue
                            else:
                                used_abilities.append(gem.ability)
                        element_set.append(gem)
                        break
                self.gem_set.append(element_set)
        if not hasattr(self, "general_controls"):
            self.general_controls = Column(
                controls=[
                    ResponsiveRow(
                        controls=[
                            Row(
                                controls=[
                                    ElevatedButton(
                                        "Min Level", on_click=self.on_min_level
                                    ),
                                    ElevatedButton(
                                        "Max Level", on_click=self.on_max_level
                                    ),
                                ],
                                col=4,
                            ),
                            Row(
                                controls=[
                                    ElevatedButton(
                                        "Min Augmentation",
                                        on_click=self.on_min_augmentation,
                                    ),
                                    ElevatedButton(
                                        "Max Augmentation",
                                        on_click=self.on_max_augmentation,
                                    ),
                                ],
                                col=4,
                            ),
                            Row(
                                controls=[
                                    ElevatedButton(
                                        "All Magic", on_click=self.on_all_magic
                                    ),
                                    ElevatedButton(
                                        "All Physical", on_click=self.on_all_physical
                                    ),
                                ],
                                col=4,
                            ),
                        ],
                        data="shortcuts_bar",
                    ),
                    ResponsiveRow(
                        controls=[
                            Switch(
                                value=True if element != element.cosmic else False,
                                label=t("gem_dragons." + element.value),
                                data=element,
                                on_change=self.on_primordial_change,
                                col=3,
                            )
                            for element in GemElement
                        ],
                        data="dragon_controls",
                    ),
                ]
            )
        if not hasattr(self, "gem_altar"):
            self.gem_altar = ResponsiveRow()
        self.gem_altar.controls = [
            Column(
                data="gem_holder",
                controls=[
                    ResponsiveRow(
                        controls=[
                            Card(
                                Container(
                                    Row(
                                        controls=[
                                            Image(
                                                BasePath.joinpath(
                                                    f"assets/images/gems/{gem.element.name}_{gem.type.name}.png"
                                                ),
                                                width=50,
                                            ),
                                            Text(
                                                f"Lvl: {gem.level} " + gem.name,
                                                size=17,
                                            ),
                                        ]
                                    ),
                                    data=gem,
                                    on_click=self.on_gem_click,
                                    border=Border(
                                        BorderSide(
                                            2,
                                            color="transparent"
                                            if self.selected_gem != gem
                                            else "green"
                                        ),
                                        BorderSide(
                                            2,
                                            color="transparent"
                                            if self.selected_gem != gem
                                            else "green"
                                        ),
                                        BorderSide(
                                            2,
                                            color="transparent"
                                            if self.selected_gem != gem
                                            else "green"
                                        ),
                                        BorderSide(
                                            2,
                                            color="transparent"
                                            if self.selected_gem != gem
                                            else "green"
                                        ),
                                    ),
                                    border_radius=6,
                                ),
                                col=4
                            )
                            for gem in gem_row
                        ],
                    )
                    for gem_row in self.gem_set
                ],
                col=6,
            ),
            Column(
                data="gem_editor",
                controls=[
                    ResponsiveRow(
                        controls=[
                            ability_editor := Column(
                                col=6
                            ),
                            level_editor := Column(
                                col=6
                            ),
                            gem_editor := Column(
                            )
                        ]
                    )
                ],
                col=6,
                disabled=self.selected_gem is None
            ),
        ]
        if isinstance(self.selected_gem, EmpoweredGem):
            unused_abilities = [
                a
                for a in self.selected_gem.possible_abilities
                if a
                not in [
                    g.ability
                    for gs in self.gem_set
                    for g in gs
                    if isinstance(g, EmpoweredGem)
                ]
            ]
            unused_abilities.append(self.selected_gem.ability)
            options = [
                dropdown.Option(key=a.name, text=t("gem_abilities." + a.value))
                for a in unused_abilities
            ]
            ability_editor.controls.append(
                Dropdown(
                    value=self.selected_gem.ability.name,
                    options=options,
                    label=t("strings.Change ability"),
                    on_change=self.on_gem_ability_change,
                    col=3,
                )
            )
        elif isinstance(self.selected_gem, LesserGem):
            ability_editor.controls.append(
                Dropdown(
                    value=self.selected_gem.restriction.value,
                    options=[dropdown.Option(r.value) for r in GemRestriction],
                    label=t("strings.Change Restriction"),
                    on_change=self.on_restriction_change,
                    col=3,
                )
            )
        else:
            ability_editor.controls.append(Dropdown(label=t("strings.Change Restriction")))
        if self.selected_gem:
            level_editor.controls.append(
                Slider(
                    min=1,
                    max=self.selected_gem.max_level,
                    value=self.selected_gem.level,
                    divisions=self.selected_gem.max_level - 1,
                    label="Level {value}",
                    on_change=self.on_gem_level_change,
                    col=8,
                )
            )
            for i, stat in enumerate(self.selected_gem.stats, 1):
                stat_row = ResponsiveRow(
                    controls=[
                        Dropdown(
                            value=stat.name.value,
                            data=stat,
                            options=[
                                dropdown.Option(s.value)
                                for s in self.selected_gem.possible_change_stats(stat)
                            ] + [dropdown.Option(stat.name.value)],
                            disabled=stat.name == Stat.light,
                            on_change=self.on_stat_change,
                            col=6
                        ),
                        Text(
                            data=stat,
                            value=f"{stat.display_percentage}"
                                  + t("strings.% Augmentation Progress"),
                            col=3
                        ),
                        Row(
                            controls=[
                                Container(
                                    Image(
                                        src=BasePath.joinpath(
                                            "assets/images/gems/augment_01.png"
                                        ),
                                        width=30,
                                    ),
                                    data=stat,
                                    on_click=self.on_rough_augment,
                                    disabled=stat.is_maxed,
                                ),
                                Container(
                                    Image(
                                        src=BasePath.joinpath(
                                            "assets/images/gems/augment_02.png"
                                        ),
                                        width=23,
                                    ),
                                    data=stat,
                                    on_click=self.on_precise_augment,
                                    disabled=stat.is_maxed,
                                ),
                                Container(
                                    Image(
                                        src=BasePath.joinpath(
                                            "assets/images/gems/augment_03.png"
                                        ),
                                        width=23,
                                    ),
                                    data=stat,
                                    on_click=self.on_superior_augment,
                                    disabled=stat.is_maxed,
                                ),
                                Container(
                                    Image(
                                        src=BasePath.joinpath(
                                            "assets/images/gems/chaosflare.png"
                                        ),
                                        width=23,
                                    ),
                                    data=stat,
                                    on_click=self.on_stat_boost_change,
                                    disabled=not bool(stat.boosts),
                                ),
                                Row(
                                    controls=[
                                         Image(
                                             src=BasePath.joinpath(
                                                 "assets/images/gems/boost.png"
                                             ),
                                             width=18,
                                         )
                                         for _ in range(stat.boosts)
                                    ] or [
                                         Image(
                                             src=BasePath.joinpath(
                                                 "assets/images/empty.png"
                                             ),
                                             width=18,
                                         )
                                    ]
                                ),
                            ],
                            col=3
                        ),
                    ],
                    col=4
                )
                gem_editor.controls.append(stat_row)
        else:
            level_editor.controls.append(
                Slider(
                    min=1,
                    max=3,
                    value=2,
                    divisions=2,
                    label="Level {value}"
                )
            )
            for i in range(3):
                stat_row = ResponsiveRow(
                    controls=[
                        Dropdown(
                            label=t("strings.Change Stat"),
                            col=6
                        )
                    ],
                    col=4
                )
                gem_editor.controls.append(stat_row)
        self.calculate_gem_report()

    def calculate_gem_report(self):
        self.gem_report.controls.clear()
        stats = {"Power Rank": [0, 0]}
        gems = [g for gs in self.gem_set for g in gs]
        dragon_controls = [
            c for c in self.general_controls.controls if c.data == "dragon_controls"
        ][0]
        for gem in gems:
            primordial = gem.element in [
                c.data for c in dragon_controls.controls if c.value
            ]
            for stat in gem.stats:
                if stat.name.value not in stats.keys():
                    stats[stat.name.value] = [0, 0]
                stats[stat.name.value][0] += stat.value * (1.1 if primordial else 1)
                stats[stat.name.value][1] += stat.max_value * (1.1 if primordial else 1)
            stats["Power Rank"][0] += gem.power_rank * (1.1 if primordial else 1)
        stats_card = Card(
            Column(
                controls=[
                    Text("Stats", size=18),
                    *[
                        Row(
                            controls=[
                                Text(value=t("stats." + stat)),
                                Text(value=str(round(value[0], 2))),
                            ]
                        )
                        for stat, value in stats.items()
                    ],
                ],
            ),
            col=4,
        )
        self.gem_report.controls.extend(
            [
                stats_card,
                Card(Text("Augmentation Costs", size=18), col=4),
                Card(Text("WIP", size=18), col=4),
            ]
        )
        asyncio.create_task(self.page.update_async())

    async def on_primordial_change(self, _):
        self.calculate_gem_report()

    async def on_gem_click(self, event):
        if self.selected_gem == event.control.data:
            self.setup_controls()
        else:
            self.setup_controls(event.control.data)
        await self.page.update_async()

    @throttle
    async def on_max_level(self, _):
        for gs in self.gem_set:
            for gem in gs:
                gem.set_level(max_levels[gem.tier.name])
        self.page.snack_bar.content.value = t("messages.maxed_gem_levels")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_min_level(self, _):
        for gs in self.gem_set:
            for gem in gs:
                gem.set_level(1)
        self.page.snack_bar.content.value = t("messages.mined_gem_levels")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_max_augmentation(self, _):
        for gs in self.gem_set:
            for gem in gs:
                for stat in gem.stats:
                    while not stat.is_maxed:
                        stat.add_superior_focus()
        self.page.snack_bar.content.value = t("messages.augmented_all_gems")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_min_augmentation(self, _):
        for gs in self.gem_set:
            for gem in gs:
                for stat in gem.stats:
                    stat.reset_augments()
        self.page.snack_bar.content.value = t("messages.deaugmented_all_gems")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_all_magic(self, _):
        for gs in self.gem_set:
            for gem in gs:
                if gem.type == GemType.lesser:
                    gem.change_restriction(GemRestriction.arcane)
                else:
                    for stat in gem.stats:
                        if stat.name == Stat.physical_damage:
                            stat.name = Stat.magic_damage
        self.page.snack_bar.content.value = t("messages.changed_all_magic")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_all_physical(self, _):
        for gs in self.gem_set:
            for gem in gs:
                if gem.type == GemType.lesser:
                    gem.change_restriction(GemRestriction.fierce)
                else:
                    for stat in gem.stats:
                        if stat.name == Stat.magic_damage:
                            stat.name = Stat.physical_damage
        self.page.snack_bar.content.value = t("messages.changed_all_physical")
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    @throttle
    async def on_gem_level_change(self, event):
        self.selected_gem.set_level(int(event.control.value))
        self.page.snack_bar.content.value = t("messages.updated_gem_level").format(
            level=self.selected_gem.level
        )
        self.page.snack_bar.open = True
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_restriction_change(self, event):
        self.selected_gem.change_restriction(GemRestriction(event.control.value))
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_gem_ability_change(self, event):
        self.selected_gem.ability = [
            a
            for a in self.selected_gem.possible_abilities
            if a.name == event.control.value
        ][0]
        self.setup_controls(self.selected_gem)
        self.page.snack_bar.content.value = t("messages.updated_ability")
        self.page.snack_bar.open = True
        await self.page.update_async()

    async def on_stat_change(self, event):
        event.control.data.name = Stat(event.control.value)
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_stat_boost_change(self, event):
        stats = [s for s in self.selected_gem.stats if s != event.control.data]
        event.control.data.move_boost_to(choice(stats))
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_rough_augment(self, event):
        event.control.data.add_rough_focus()
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_precise_augment(self, event):
        event.control.data.add_precise_focus()
        self.setup_controls(self.selected_gem)
        await self.page.update_async()

    async def on_superior_augment(self, event):
        event.control.data.add_superior_focus()
        self.setup_controls(self.selected_gem)
        await self.page.update_async()
