import base64
from datetime import datetime, timedelta

from flet import Text, Column, Row, Card, ResponsiveRow, Image, Stack, Divider

from models.objects import Controller
from utils import tasks
from json import load
import requests
from pytz import UTC


class Widget(Card):
    def __init__(self):
        self.widget_content = Row(
            controls=[],
            alignment="center",
            spacing=70,
        )
        self.widget_controls = self.widget_content.controls
        super().__init__(
            content=Column(
                controls=[
                    self.widget_content
                ],
                horizontal_alignment="center",
            ),
            height=190,
            col={"xxl": 2.5}
        )

class HomeController(Controller):
    def setup_controls(self):
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
        self.daily_widget = Widget()
        self.weekly_widget = Widget()
        self.next_daily_widget = Widget()
        self.next_weekly_widget = Widget()
        self.widgets = ResponsiveRow(
            controls=[
                self.clock_widget,
                Row(
                    controls=[
                        Text("This week", size=20),
                        Divider()
                    ],
                ),
                self.daily_widget,
                self.weekly_widget,
                Row(
                    controls=[
                        Text("Next week", size=20),
                        Divider()
                    ],
                ),
                self.next_daily_widget,
                self.next_weekly_widget,
            ],
            spacing=40
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
            daily_data = load(open("data/daily_buffs.json", encoding="utf-8"))
            daily = daily_data[str(now.weekday())]
            banner = base64.b64encode(requests.get(daily["banner"]).content)
            self.daily_widget.widget_controls = [
                Stack(
                    controls=[
                        Image(src_base64=banner.decode("utf-8"), expand=True),
                        Text(daily["name"], size=19, top=9, left=10),
                        *[
                            Column(
                                controls=[
                                    Text(
                                        buff,
                                        size=9 if buff != "Normal Buffs" else 12,
                                        weight="bold" if buff == "Normal Buffs" else None
                                    )
                                ],
                                width=260,
                                left=10,
                                bottom=16 * (i + 4)
                            )
                            for i, buff in enumerate(daily["normal_buffs"] + ["Normal Buffs"])
                        ],
                        *[
                            Column(
                                controls=[
                                    Text(
                                        buff,
                                        size=9 if buff != "Patron Buffs" else 12,
                                        weight="bold" if buff == "Patron Buffs" else None
                                    )
                                ],
                                width=260,
                                left=10,
                                bottom=16 * i
                            )
                            for i, buff in enumerate(daily["premium_buffs"] + ["Patron Buffs"])
                        ]
                    ],
                    height=180
                ),
            ]
            await self.weekly_widget.update_async()
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
        weekly_data = load(open("data/weekly_buffs.json", encoding="utf-8"))
        weekly = weekly_data[str(int(time_find))]
        banner = base64.b64encode(requests.get(weekly["banner"]).content)
        self.weekly_widget.widget_controls = [
            Stack(
                controls=[
                    Image(src_base64=banner.decode("utf-8"), expand=True),
                    Text(weekly["name"], size=19, top=10, left=10),
                    *[
                        Column(controls=[Text(buff)], width=260, left=10, bottom=25*(i+1))
                        for i, buff in enumerate(weekly["buffs"])
                    ]
                ]
            ),
        ]
        await self.weekly_widget.update_async()
