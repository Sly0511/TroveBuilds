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
    TextField,
    TextStyle,
    Border,
    BorderSide,
    Dropdown,
    dropdown,
    Slider,
    Switch,
)
from i18n import t

from models.objects import Controller
from models.objects.gem import (
    LesserGem,
    EmpoweredGem,
    GemElement,
    GemTier,
    GemRestriction,
    Stat,
)
from utils.calculations.gems import get_stat_values
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
            self.gem_holder = ResponsiveRow()
            self.gem_editor = ResponsiveRow(expand=True, visible=False)
        else:
            self.gem_holder.controls.clear()
            self.gem_editor.controls.clear()
        if not hasattr(self, "general_controls"):
            self.general_controls = ResponsiveRow(
                controls=[
                    Switch(
                        value=True if element != element.cosmic else False,
                        label=t("gem_dragons." + element.value),
                        data=element,
                        on_change=self.on_primordial_change,
                        col=3,
                    )
                    for element in GemElement
                ]
            )
        self.gem_controls = []
        for gem_row in self.gem_set:
            row = ResponsiveRow(expand=True)
            for gem in gem_row:
                gem_control = Card(
                    Container(
                        Row(
                            controls=[
                                Image(
                                    BasePath.joinpath(
                                        f"assets/images/gems/{gem.element.name}_{gem.type.name}.png"
                                    ),
                                    width=50,
                                ),
                                Text(gem.name, size=20),
                            ]
                        ),
                        data=gem,
                        on_click=self.on_gem_click,
                        border=Border(
                            BorderSide(
                                2,
                                color="transparent"
                                if self.selected_gem != gem
                                else "green",
                            ),
                            BorderSide(
                                2,
                                color="transparent"
                                if self.selected_gem != gem
                                else "green",
                            ),
                            BorderSide(
                                2,
                                color="transparent"
                                if self.selected_gem != gem
                                else "green",
                            ),
                            BorderSide(
                                2,
                                color="transparent"
                                if self.selected_gem != gem
                                else "green",
                            ),
                        ),
                        border_radius=6,
                    ),
                    col=4,
                )
                row.controls.append(gem_control)
                self.gem_controls.append(gem_control)
            self.gem_holder.controls.append(row)
        self.calculate_gem_report()

    def calculate_gem_report(self):
        self.gem_report.controls.clear()
        stats = {}
        gems = [g for gs in self.gem_set for g in gs]
        for gem in gems:
            primordial = gem.element in [
                c.data for c in self.general_controls.controls if c.value
            ]
            for stat in gem.stats:
                min_value, max_value, diff = get_stat_values(
                    gem.tier.name,
                    gem.type.name,
                    stat.name.value,
                    gem.level,
                    stat.boosts,
                )
                value = min_value + diff * stat.percentage
                if stat.name.value not in stats.keys():
                    stats[stat.name.value] = [0, 0]
                stats[stat.name.value][0] += value * (1.1 if primordial else 1)
                stats[stat.name.value][1] += max_value * 1.1
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

    async def on_primordial_change(self, event):
        self.calculate_gem_report()

    async def on_gem_click(self, event):
        for gem_control in self.gem_controls:
            if event.control != gem_control.content:
                gem_control.content.border.top.color = "transparent"
                gem_control.content.border.bottom.color = "transparent"
                gem_control.content.border.left.color = "transparent"
                gem_control.content.border.right.color = "transparent"
        if self.selected_gem == event.control.data:
            event.control.border.top.color = "transparent"
            event.control.border.bottom.color = "transparent"
            event.control.border.left.color = "transparent"
            event.control.border.right.color = "transparent"
            self.selected_gem = None
            self.gem_editor.controls = []
            self.gem_editor.visible = False
        else:
            event.control.border.top.color = "green"
            event.control.border.bottom.color = "green"
            event.control.border.left.color = "green"
            event.control.border.right.color = "green"
            self.selected_gem = event.control.data
            await self.build_editor()
            self.gem_editor.visible = True
        await self.page.update_async()

    async def build_editor(self):
        self.gem_editor.controls.clear()
        self.gem_editor.controls.append(meta_row := ResponsiveRow(controls=[]))
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
            options = [
                dropdown.Option(key=a.name, text=t("gem_abilities." + a.value))
                for a in unused_abilities
            ]
            meta_row.controls.append(
                Dropdown(
                    options=options,
                    label=t("gem_abilities." + self.selected_gem.ability.value),
                    on_change=self.on_gem_ability_change,
                    col=4,
                )
            )
        elif isinstance(self.selected_gem, LesserGem):
            restricition = (
                GemRestriction.arcane.value
                if self.selected_gem.restriction != GemRestriction.arcane
                else GemRestriction.fierce.value
            )
            meta_row.controls.append(
                Dropdown(
                    options=[dropdown.Option(restricition)],
                    label=t("gem_restrictions." + self.selected_gem.restriction.value),
                    on_change=self.on_restriction_change,
                    col=4,
                )
            )
        meta_row.controls.append(
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
            options = [
                dropdown.Option(s.value)
                for s in self.selected_gem.possible_change_stats
            ]
            stat_select = Dropdown(
                data=stat,
                label=t("stats." + stat.name.value),
                options=options,
                disabled=stat.name.value == Stat.light.value,
                on_change=self.on_stat_change,
            )
            stat_row = ResponsiveRow(
                controls=[
                    stat_select,
                    Text(
                        data=stat,
                        value=f"{stat.display_percentage}" + t("strings.% Augmentation Progress")
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
                                    width=30,
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
                                    width=30,
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
                                    width=30,
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
                                        width=25,
                                    )
                                    for _ in range(stat.boosts)
                                ]
                                or [
                                    Image(
                                        src=BasePath.joinpath(
                                            "assets/images/empty.png"
                                        ),
                                        width=25,
                                    )
                                ]
                            ),
                        ]
                    ),
                ],
                col=4,
                expand=True,
            )
            self.gem_editor.controls.append(stat_row)

    @throttle
    async def on_gem_level_change(self, event):
        self.selected_gem.set_level(int(event.control.value))
        self.page.snack_bar.content.value = t("messages.updated_gem_level").format(
            level=self.selected_gem.level
        )
        self.page.snack_bar.open = True
        await self.build_editor()
        await self.page.update_async()

    async def on_restriction_change(self, event):
        self.selected_gem.change_restriction(GemRestriction(event.control.value))
        self.setup_controls(self.selected_gem)
        await self.build_editor()
        await self.page.update_async()

    async def on_gem_ability_change(self, event):
        self.selected_gem.ability = [
            a
            for a in self.selected_gem.possible_abilities
            if a.name == event.control.value
        ][0]
        self.setup_controls(self.selected_gem)
        await self.build_editor()
        self.page.snack_bar.content.value = t("messages.updated_ability")
        self.page.snack_bar.open = True
        await self.page.update_async()

    async def on_stat_change(self, event):
        event.control.data.name = Stat(event.control.value)
        self.setup_controls(self.selected_gem)
        await self.build_editor()
        await self.page.update_async()

    async def on_stat_boost_change(self, event):
        stats = [s for s in self.selected_gem.stats if s != event.control.data]
        event.control.data.move_boost_to(choice(stats))
        self.setup_controls(self.selected_gem)
        await self.build_editor()
        await self.page.update_async()

    async def on_rough_augment(self, event):
        event.control.data.add_rough_focus()
        await self.build_editor()
        await self.page.update_async()

    async def on_precise_augment(self, event):
        event.control.data.add_precise_focus()
        await self.build_editor()
        await self.page.update_async()

    async def on_superior_augment(self, event):
        event.control.data.add_superior_focus()
        await self.build_editor()
        await self.page.update_async()
