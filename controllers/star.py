from flet import (
    ElevatedButton,
    Stack,
    Column,
    Text,
    ResponsiveRow,
    canvas,
    Paint,
    PaintingStyle,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    Container,
    Divider
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
        self.star_details = Column(
            col={"xxl": 2},
        )
        self.map.controls.extend(
            [
                ScrollingFrame(
                    content=canvas.Canvas(
                        content=Stack(
                            controls=[
                                Text(
                                    f"{self.star_chart.activated_stars_count}/{self.star_chart.max_nodes}",
                                    size=40,
                                    left=30
                                ),
                                ElevatedButton(
                                    "Reset",
                                    top=50,
                                    left=40,
                                    on_click=self.reset_chart
                                ),
                                *[
                                    RoundButton(
                                        data=star,
                                        size=12 if star.type == StarType.minor else 20,
                                        bgcolor=star.color,
                                        left=star.coords[0],
                                        top=star.coords[1],
                                        on_click=self.change_lock_status,
                                        on_hover=self.show_star_details
                                    )
                                    for star in self.star_chart.get_stars()
                                ],
                            ],
                            width=700,
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
                        width=700,
                        height=850,
                    ),
                    col={"xxl": 5},
                ),
                self.star_details,
                Column(
                    controls=[
                        Text("Stats", size=22),
                        *([
                              DataTable(
                                  heading_row_height=0,
                                  data_row_height=30,
                                  columns=[
                                      DataColumn(Text()),
                                      DataColumn(Text())
                                  ],
                                  rows=[
                                      DataRow(
                                          cells=[
                                              DataCell(Text(k)),
                                              DataCell(Text(str(v[0]) + (f"%" if v[1] else "")))
                                          ]
                                      )
                                      for k, v in self.star_chart.activated_stats.items()
                                  ]
                              )
                        ] if self.star_chart.activated_stats else [Text("-")])
                    ],
                    col={"xxl": 2},
                ),
                Column(
                    controls=[
                        Text("Abilities", size=22),
                        *([
                              Text(a)
                              for a in self.star_chart.activated_abilities
                          ] or [Text("-")]),
                        Text("Obtainables", size=22),
                        *([
                              Text(f"{v}x  {k}")
                              for k, v in self.star_chart.activated_obtainables.items()
                          ] or [Text("-")])
                    ],
                    col={"xxl": 3},
                )
            ]
        )

    def setup_events(self):
        ...

    async def change_lock_status(self, event):
        staged_lock = event.control.data.stage_lock(self.star_chart)
        if staged_lock <= 0:
            event.control.data.switch_lock()
        else:
            self.page.snack_bar.bgcolor = "red"
            self.page.snack_bar.content.value = f"Activating this star exceeds max of {self.star_chart.max_nodes}" \
            f" by {staged_lock}"
            self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()
        self.page.snack_bar.bgcolor = "green"

    async def reset_chart(self, _):
        self.star_chart = get_star_chart()
        self.setup_controls()
        await self.page.update_async()

    async def show_star_details(self, event):
        star = event.control.data
        if event.data == "true":
            self.star_details.controls = [
                Column(
                    controls=[
                        Column(
                            controls=[
                                Text(star.full_name, text_align="center", size=20)
                            ],
                            alignment="center",
                            horizontal_alignment="center"
                        ),
                        Column(
                            controls=[
                                *(
                                    [
                                        Divider(),
                                        Text("Stats", size=14),
                                        DataTable(
                                            heading_row_height=0,
                                            data_row_height=30,
                                            columns=[
                                                DataColumn(Text()),
                                                DataColumn(Text())
                                            ],
                                            rows=[
                                                DataRow(
                                                    cells=[
                                                        DataCell(Text(k)),
                                                        DataCell(Text(str(v[0]) + (f"%" if v[1] else "")))
                                                    ]
                                                )
                                                for k, v in star.format_stats.items()
                                            ]
                                        )
                                    ] if star.stats else []
                                ),
                                *(
                                    [
                                        Divider(),
                                        Text("Abilities", size=14),
                                        DataTable(
                                            heading_row_height=0,
                                            data_row_height=80,
                                            columns=[
                                                DataColumn(Text())
                                            ],
                                            rows=[
                                                DataRow(
                                                    cells=[
                                                        DataCell(Text(v))
                                                    ]
                                                )
                                                for v in star.abilities
                                            ]
                                        )
                                    ] if star.abilities else []
                                ),
                                *(
                                    [
                                        Divider(),
                                        Text("Obtainables", size=14),
                                        DataTable(
                                            heading_row_height=0,
                                            data_row_height=50,
                                            columns=[
                                                DataColumn(Text())
                                            ],
                                            rows=[
                                                DataRow(
                                                    cells=[
                                                        DataCell(Text(v))
                                                    ]
                                                )
                                                for v in star.obtainables
                                            ]
                                        )
                                    ] if star.obtainables else []
                                )
                            ]
                        )
                    ]
                )
            ]
        else:
            self.star_details.controls.clear()
        await self.star_details.update_async()
