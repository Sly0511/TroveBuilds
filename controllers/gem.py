import asyncio
from copy import copy
from random import choice

import flet_core.colors
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
    ElevatedButton,
    Draggable,
    DragTarget,
    DataTable,
    DataRow,
    DataColumn,
    DataCell,
    Tabs,
    Tab,
    Stack,
    VerticalDivider,
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
from utils.data.gems import max_levels, augment_costs
from utils.functions import throttle
from utils.path import BasePath


class GemController(Controller):
    def setup_controls(self, gem=None, stat=None):
        if not hasattr(self, "selected_gem"):
            self.selected_gem = LesserGem.random_gem()
        if gem:
            self.selected_gem = gem
        if not hasattr(self, "selected_stat"):
            self.selected_stat = None
        if not hasattr(self, "header_row"):
            self.header_row = ResponsiveRow()
        self.header_row.controls.clear()
        self.header_row.controls.append(
            Column(
                controls=[
                    Row(
                        controls=[
                            ElevatedButton(text=t("gem_tiers.Radiant"), on_click=self.reroll_radiant),
                            ElevatedButton(text=t("gem_tiers.Stellar"), on_click=self.reroll_stellar),
                            ElevatedButton(text=t("gem_tiers.Crystal"), on_click=self.reroll_crystal),
                        ],
                        alignment="center",
                    ),
                    Text(
                        value=self.selected_gem.name
                    ),
                    DragTarget(
                        content=Stack(
                            controls=[
                                Image(
                                    f"assets/images/rarity/{self.selected_gem.tier.name}_frame.png",
                                    scale=1.66,
                                    left=90,
                                    top=87,
                                ),
                                Image(
                                    f"assets/images/gems/old_{self.selected_gem.element.name}_{self.selected_gem.type.name}.png",
                                    scale=0.4,
                                ),
                            ]
                        ),
                    ),
                    *[
                        Stack(
                            controls=[
                                Container(
                                    Card(
                                        Container(
                                            Column(
                                                controls=[
                                                    Row(
                                                        controls=[
                                                            Text(
                                                                str(round(stat.value, 3)),
                                                                color="green",
                                                            ),
                                                            Text(
                                                                t(f"stats.{stat.name.value}"),
                                                                weight="bold",
                                                            ),
                                                            Text(
                                                                f"({stat.display_percentage}%)",
                                                                expand=True,
                                                                color=(
                                                                    "red"
                                                                    if stat.percentage
                                                                       < 1 / 3
                                                                    else (
                                                                        "yellow"
                                                                        if stat.percentage
                                                                           < 1 / 3 * 2
                                                                        else "green"
                                                                    )
                                                                ),
                                                            ),
                                                            Text(
                                                                f"{stat.min_value} - {stat.max_value}"
                                                            ),
                                                        ],
                                                    ),
                                                    ResponsiveRow(
                                                        controls=[
                                                            *[
                                                                Container(
                                                                    Text(f"{round(container.percentage * 100, 2)}%",
                                                                         text_align="center"),
                                                                    border=Border(
                                                                        *(
                                                                                [BorderSide(2, "blue")]
                                                                                * 4
                                                                        )
                                                                    ),
                                                                    border_radius=0,
                                                                    col=3
                                                                )
                                                                for container in stat.containers
                                                            ],
                                                            *[
                                                                Container(
                                                                    Text(text_align="center"),
                                                                    border=Border(
                                                                        *(
                                                                                [BorderSide(2, "black")]
                                                                                * 4
                                                                        )
                                                                    ),
                                                                    border_radius=0,
                                                                    col=3
                                                                )
                                                                for _ in range(3 - stat.boosts)
                                                            ]
                                                        ],
                                                        spacing=0
                                                    )
                                                ]
                                            ),
                                            padding=18,
                                            border=Border(
                                                *(
                                                        [BorderSide(2,
                                                                    "transparent" if stat != self.selected_stat else "green")]
                                                        * 4
                                                )
                                            ),
                                            border_radius=5,
                                            disabled=not bool(self.selected_gem),
                                            on_click=self.select_stat,
                                            data=stat
                                        )
                                    ),
                                ),
                                *[
                                    Image(
                                        "assets/images/gems/boost.png",
                                        width=18,
                                        left=20 * i,
                                        top=0,
                                    )
                                    for i in range(stat.boosts)
                                ],
                            ],
                        )
                        for stat in self.selected_gem.stats
                    ],
                    ResponsiveRow(
                        controls=[
                            Text("Improve Stat", col=5.5, text_align="right"),
                            Container(col=2.2),
                            Text("Reroll Stat", col=4.3, text_align="left"),
                        ],
                        alignment="center"
                    ),
                    Container(height=5),
                    ResponsiveRow(
                        controls=[
                            Container(
                                content=Image("assets/images/gems/augment_01.png", width=40),
                                disabled=not bool(self.selected_stat),
                                on_click=self.rough_augment,
                                col=1.5
                            ),
                            Container(
                                content=Image("assets/images/gems/augment_02.png", width=40),
                                disabled=not bool(self.selected_stat),
                                on_click=self.precise_augment,
                                col=1.5
                            ),
                            Container(
                                content=Image("assets/images/gems/augment_03.png", width=40),
                                disabled=not bool(self.selected_stat),
                                on_click=self.superior_augment,
                                col=1.5
                            ),
                            Container(
                                width=20,
                                col=1
                            ),
                            Container(
                                content=Image("assets/images/gems/chaosspark.png", width=43),
                                disabled=not bool(self.selected_stat) or [s for s in self.selected_gem.stats if s.name == stat.light],
                                on_click=self.change_stat,
                                col=1.5
                            ),
                            Container(
                                content=Image("assets/images/gems/chaosflare.png", width=43),
                                disabled=not bool(self.selected_stat) or not stat.boosts,
                                on_click=self.move_boost,
                                col=1.5
                            )
                        ],
                        alignment="center"
                    ),
                    ResponsiveRow(
                        controls=[
                            Container(
                                content=Text("2.5%"),
                                col=1.5
                            ),
                            Container(
                                content=Text("5.0%"),
                                col=1.5
                            ),
                            Container(
                                content=Text("12.5%"),
                                col=1.5
                            ),
                            Container(
                                width=20,
                                col=1
                            ),
                            Container(
                                content=Text("Change Stat", size=10, text_align="center"),
                                col=1.5
                            ),
                            Container(
                                content=Text("Move Boost", size=10, text_align="center"),
                                col=1.5
                            )
                        ],
                        alignment="center"
                    )
                ],
                horizontal_alignment="center",
                col=3,
            )
        )
        asyncio.create_task(self.page.update_async())

    def setup_events(self):
        ...

    async def select_stat(self, event):
        if self.selected_stat == event.control.data:
            self.selected_stat = None
        else:
            self.selected_stat = event.control.data
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def reroll_radiant(self, _):
        self.setup_controls(LesserGem.random_gem(GemTier.radiant), None)

    async def reroll_stellar(self, _):
        self.setup_controls(LesserGem.random_gem(GemTier.stellar), None)

    async def reroll_crystal(self, _):
        self.setup_controls(LesserGem.random_gem(GemTier.crystal), None)

    async def rough_augment(self, _):
        self.selected_stat.add_rough_focus()
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def precise_augment(self, _):
        self.selected_stat.add_precise_focus()
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def superior_augment(self, _):
        self.selected_stat.add_superior_focus()
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def change_stat(self, _):
        possible_stats = [s for s in self.selected_gem.possible_change_stats(self.selected_stat)]
        self.selected_stat.name = choice(possible_stats)
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def move_boost(self, _):
        stats = [s for s in self.selected_gem.stats if s != self.selected_stat]
        self.selected_stat.move_boost_to(choice(stats))
        self.setup_controls(self.selected_gem, self.selected_stat)

    async def copy_to_clipboard(self, event):
        if value := event.control.content.value:
            await self.page.set_clipboard_async(str(value))
            self.page.snack_bar.content.value = "Copied to clipboard"
            self.page.snack_bar.open = True
        await self.page.update_async()
