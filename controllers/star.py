from flet import ElevatedButton, Stack, Container, Text, Image, ImageFit, Tooltip, Column, Row, Divider
from utils.star_chart import get_star_chart, Star, StarType
from math import radians, cos, sin


from models.objects import Controller


class RoundButton(ElevatedButton):
    def __init__(self, size=20, bgcolor="blue", **kwargs):
        super().__init__(width=size, height=size, bgcolor=bgcolor, **kwargs)


class StarChartController(Controller):
    def setup_controls(self):
        star_chart = get_star_chart()
        self.map = Stack(
            controls=[
                Image("assets/images/star_chart/chart.jpg", width=800*2, top=0, left=-340),
                *[
                    RoundButton(
                        size=20 if star.type == StarType.minor else 28,
                        bgcolor="blue" if star.type == StarType.root else ("red" if star.type == StarType.minor else "yellow"),
                        left=star.coords[0],
                        top=star.coords[1],
                        tooltip=star.full_name
                    )
                    for star in star_chart.get_stars()
                ]
            ],
            expand=True,
        )

    def setup_events(self):
        ...
