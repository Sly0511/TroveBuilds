from flet import View, Icon, Text, Column, Card, ResponsiveRow, Row
from flet_core.icons import HOME_SHARP

from utils.controls import TroveToolsAppBar
from utils import tasks
from datetime import datetime, timedelta


class HomeView(View):
    def __init__(self, page):
        self.title = Text("Home")
        self.icon = Icon(HOME_SHARP)
        self.date = Text("Trove Time", size=20)
        self.clock = Text("Trove Time", size=20)
        super().__init__(
            route="/",
            controls=[
                Column(
                    controls=[
                        ResponsiveRow(
                            controls=[
                                Card(
                                    content=Column(
                                        controls=[
                                            Text("Trove Time", size=24),
                                            Row(
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
                                    col=3,
                                )
                            ],
                            spacing=40,
                        )
                    ],
                    alignment="center",
                )
            ],
        )
        self.update_clock.start()

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
