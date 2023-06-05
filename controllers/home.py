import asyncio
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
    LinearGradient,
    alignment,
    Tooltip,
    Border,
    BorderSide,
    BlendMode
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
        if not hasattr(self, "widgets"):
            self.widgets = ResponsiveRow(
                spacing=40,
            )
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
            col={"xxl": 2.5}
        )
        self.daily_widgets = Column(
            controls=[
                Widget(
                    data=k,
                    controls=[
                        Tooltip(
                            message="\n".join(
                                [
                                    "Normal",
                                    *[
                                        " \u2022 " + b
                                        for b in v["normal_buffs"]
                                    ],
                                    "Patreon",
                                    *[
                                        " \u2022 " + b
                                        for b in v["premium_buffs"]
                                    ],
                                ]
                            ),
                            content=Stack(
                                controls=[
                                    Image(
                                        color="black",
                                        src_base64=base64.b64encode(
                                            requests.get(v["banner"]).content
                                        ).decode("utf-8")
                                    ),
                                    Container(
                                        gradient=LinearGradient(
                                            begin=alignment.center_left,
                                            end=alignment.center_right,
                                            colors=[
                                                "#ff000000",
                                                "#00000000",
                                            ],
                                        ),
                                        width=200,
                                        height=46,
                                    ),
                                    Text(
                                        v["weekday"],
                                        color="#cccccc",
                                        left=10,
                                        top=3,
                                        size=16
                                    ),
                                    Text(
                                        v["name"],
                                        color="#cccccc",
                                        left=10,
                                        top=23,
                                    )
                                ]
                            ),
                            border_radius=10,
                            bgcolor="#1E1E28",
                            text_style=TextStyle(color="#cccccc"),
                            border=Border(
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"])
                            ),
                            prefer_below=False,
                            wait_duration=250
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
                        Tooltip(
                            message="\n".join(
                                [
                                    "Buffs",
                                    *[
                                        " \u2022 " + b
                                        for b in v["buffs"]
                                    ]
                                ]
                            ),
                            content=Stack(
                                controls=[
                                    Image(
                                        color="black",
                                        src_base64=base64.b64encode(
                                            requests.get(v["banner"]).content
                                        ).decode("utf-8")
                                    ),
                                    Container(
                                        gradient=LinearGradient(
                                            begin=alignment.center_left,
                                            end=alignment.center_right,
                                            colors=[
                                                "#ff000000",
                                                "#00000000",
                                            ],
                                        ),
                                        width=200,
                                        height=182,
                                    ),
                                    Text(
                                        v["name"],
                                        color="#cccccc",
                                        size=16,
                                        left=10,
                                        top=3,
                                    )
                                ]
                            ),
                            border_radius=10,
                            bgcolor="#1E1E28",
                            text_style=TextStyle(color="#cccccc"),
                            border=Border(
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"]),
                                BorderSide(width=2, color="#" + v["color"])
                            ),
                            prefer_below=False,
                            wait_duration=250
                        )
                    ],
                    col={"xxl": 6}
                )
                for k, v in self.weekly_data.items()
            ],
        )
        self.widgets.controls = [
            self.clock_widget,
            Container(),
            Column(
                controls=[
                    Text("Daily Buffs", size=20),
                    self.daily_widgets
                ],
                col={"xxl": 3}
            ),
            Column(
                controls=[
                    Text("Weekly buffs", size=20),
                    self.weekly_widgets
                ],
                col={"xxl": 5}
            )
        ]
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
        await asyncio.sleep(3)
        try:
            now = datetime.utcnow() - timedelta(hours=11)
            for control in self.daily_widgets.controls:
                stack = control.content.controls[0].content
                if int(control.data) == now.weekday():
                    stack.controls[0].color = None
                    stack.controls[0].color_blend_mode = None
                else:
                    stack.controls[0].color = "black"
                    stack.controls[0].color_blend_mode = BlendMode.SATURATION
            await self.daily_widgets.update_async()
        except Exception as e:
            print(e)

    @tasks.loop(seconds=60)
    async def update_weekly(self):
        await asyncio.sleep(3)
        initial = datetime(2020, 3, 30, tzinfo=UTC) - timedelta(hours=11)
        now = datetime.utcnow() - timedelta(hours=11)
        week_length = 60 * 60 * 24 * 7
        weeks = (now.timestamp() - initial.timestamp()) // week_length
        time_split = weeks / 4
        time_find = (time_split - int(time_split)) * 4
        for control in self.weekly_widgets.controls:
            stack = control.content.controls[0].content
            if int(control.data) == int(time_find):
                stack.controls[0].color = None
                stack.controls[0].color_blend_mode = None
            else:
                stack.controls[0].color = "black"
                stack.controls[0].color_blend_mode = BlendMode.SATURATION
        await self.weekly_widgets.update_async()
