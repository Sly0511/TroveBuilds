import base64
from datetime import datetime, timedelta
from json import load

import requests
from flet import (
    Text,
    Column,
    Row,
    Container,
    Card,
    ResponsiveRow,
    Image,
    Stack,
    Divider,
    TextStyle,
    BoxShadow,
    TextSpan,
)
from pytz import UTC

from models.objects import Controller
from utils import tasks


class Widget(Container):
    def __init__(self, controls: list = [], **kwargs):
        super().__init__(
            content=Column(
                controls=[*controls],
                horizontal_alignment="center",
            ),
            on_hover=None,
            **kwargs
        )


class HomeController(Controller):
    def setup_controls(self):
        self.daily_data = load(open("data/daily_buffs.json", encoding="utf-8"))
        self.weekly_data = load(open("data/weekly_buffs.json", encoding="utf-8"))
        self.date = Text("Trove Time", size=20, col={"xxl": 6})
        self.clock = Text("Trove Time", size=20, col={"xxl": 6})
        self.clock_widget = Card(
            content=Column(
                controls=[
                    Text("Trove Time", size=24),
                    ResponsiveRow(
                        controls=[
                            self.date,
                            self.clock,
                        ],
                        alignment="center",
                        spacing=70,
                    ),
                ],
                horizontal_alignment="center",
            ),
            height=190,
            col={"xxl": 2.5},
        )
        self.daily_widgets = Column(
            controls=[
                Widget(
                    data=k,
                    controls=[
                        Stack(
                            controls=[
                                Image(
                                    src_base64=base64.b64encode(
                                        requests.get(v["banner"]).content
                                    ).decode("utf-8")
                                ),
                                Container(
                                    TextSpan(
                                        v["weekday"],
                                        style=TextStyle(
                                            color="#" + v["color"],
                                            shadow=BoxShadow(color="black"),
                                            size=16,
                                        ),
                                    ),
                                    left=10,
                                    top=3,
                                ),
                                Text(
                                    v["name"],
                                    color="#" + v["color"],
                                    left=10,
                                    top=23,
                                    size=16,
                                ),
                                # *[
                                #     Text(
                                #         buff,
                                #         left=10 if buff in ["Buffs", "Patron Buffs"] else 15,
                                #         size=8 if buff not in ["Buffs", "Patron Buffs"] else 10,
                                #         top=22+14*i,
                                #         weight="bold" if buff in ["Buffs", "Patron Buffs"] else None
                                #     )
                                #     for i, buff in enumerate(
                                #         ["Buffs"] + v["normal_buffs"] + ["Patron Buffs"] + v["premium_buffs"], 1
                                #     )
                                # ]
                            ]
                        )
                    ],
                )
                for k, v in self.daily_data.items()
            ],
        )
        self.weekly_widgets = ResponsiveRow(
            controls=[
                Widget(
                    data=k,
                    controls=[
                        Stack(
                            controls=[
                                Image(
                                    src_base64=base64.b64encode(
                                        requests.get(v["banner"]).content
                                    ).decode("utf-8")
                                ),
                                Text(v["name"], left=10, size=16),
                                *[
                                    Text(
                                        buff,
                                        left=10 if buff in ["Buffs"] else 15,
                                        size=10 if buff not in ["Buffs"] else 12,
                                        top=11 + 25 * i,
                                        weight="bold" if buff in ["Buffs"] else None,
                                    )
                                    for i, buff in enumerate(["Buffs"] + v["buffs"], 1)
                                ],
                            ]
                        )
                    ],
                    col={"xxl": 12 / len(self.weekly_data.values())},
                )
                for k, v in self.weekly_data.items()
            ]
        )
        self.next_daily_widget = Widget()
        self.next_weekly_widget = Widget()
        self.widgets = ResponsiveRow(
            controls=[
                self.clock_widget,
                Row(
                    controls=[Text("Daily Buffs", size=20), Divider()],
                ),
                self.daily_widgets,
                Row(
                    controls=[Text("Weekly buffs", size=20), Divider()],
                ),
                self.weekly_widgets,
            ],
            spacing=40,
        )
        self.update_clock.start()
        self.update_daily.start()
        self.update_weekly.start()

    def setup_events(self):
        ...

    @tasks.loop(seconds=1)
    async def update_clock(self):
        now = datetime.utcnow() - timedelta(hours=11)
        self.date.value = now.strftime("%Y-%m-%d")
        self.clock.value = now.strftime("%H:%M:%S")
        try:
            await self.date.update_async()
            await self.clock.update_async()
        except Exception:
            ...

    @tasks.loop(seconds=60)
    async def update_daily(self):
        try:
            now = datetime.utcnow() - timedelta(hours=11)
            self.daily_widgets.controls[now.weekday()].bg_color = "yellow"
            await self.page.update_async()
        except Exception as e:
            print(e)

    @tasks.loop(seconds=60)
    async def update_weekly(self):
        initial = datetime(2020, 3, 23, tzinfo=UTC) - timedelta(hours=11)
        now = datetime.utcnow() - timedelta(hours=11)
        week_length = 60 * 60 * 24 * 7
        weeks = (now.timestamp() - initial.timestamp()) // week_length
        time_split = weeks / 4
        time_find = (time_split - int(time_split)) * 4
        self.weekly_widgets.controls[int(time_find)].bg_color = "yellow"
        await self.page.update_async()
