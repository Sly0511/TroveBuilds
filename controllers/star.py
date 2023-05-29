from flet import (
    ElevatedButton,
    Stack,
    Column,
    Text,
    ResponsiveRow,
    canvas,
    Paint,
    PaintingStyle,
)

from models.objects import Controller
from utils.star_chart import get_star_chart, StarType
from utils.controls.scrolling import ScrollingFrame


class RoundButton(ElevatedButton):
    def __init__(self, size=20, bgcolor="blue", **kwargs):
        super().__init__(width=size, height=size, bgcolor=bgcolor, **kwargs)


class StarChartController(Controller):
    def setup_controls(self):
        if not hasattr(self, "map"):
            self.star_chart = get_star_chart()
            self.map = ResponsiveRow()
        self.map.controls.clear()
        self.map.controls.extend(
            [
                ScrollingFrame(
                    content=canvas.Canvas(
                        content=Stack(
                            controls=[
                                *[
                                    RoundButton(
                                        data=star,
                                        size=12 if star.type == StarType.minor else 20,
                                        bgcolor=star.color,
                                        left=star.coords[0],
                                        top=star.coords[1],
                                        tooltip=star.full_name,
                                        on_click=self.change_lock_status,
                                    )
                                    for star in self.star_chart.get_stars()
                                ],
                            ],
                            width=800,
                            height=850,
                        ),
                        shapes=[
                            *[
                                canvas.Path(
                                    [
                                        canvas.Path.MoveTo(*star.angle[0]),
                                        canvas.Path.LineTo(*star.angle[1]),
                                    ],
                                    paint=Paint(
                                        stroke_width=2,
                                        style=PaintingStyle.STROKE,
                                        color="#aabbcc"
                                        if not star.unlocked
                                        else "#ffd400",
                                    ),
                                )
                                for star in self.star_chart.get_stars()
                                if star.angle
                            ]
                        ],
                        width=800,
                        height=850,
                    ),
                    col={"xxl": 6},
                ),
                Column(
                    controls=[
                        Text("Star"),
                        Text("Star"),
                        Text("Star"),
                        Text("Star"),
                    ],
                    col={"xxl": 3},
                ),
                Column(
                    controls=[
                        Text("Star"),
                        Text("Star"),
                        Text("Star"),
                        Text("Star"),
                    ],
                    col={"xxl": 3},
                ),
            ]
        )

    def setup_events(self):
        ...

    async def change_lock_status(self, event):
        if event.control.data.stage_lock(self.star_chart):
            event.control.data.switch_lock()
        else:
            self.page.snack_bar.bgcolor = "red"
            self.page.snack_bar.content.value = f"You can't exceed the maximum nodes of {self.star_chart.max_nodes}"
            self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()
        self.page.snack_bar.bgcolor = "green"
