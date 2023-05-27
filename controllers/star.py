from flet import (
    ElevatedButton,
    Stack,
    Container,
    Text,
    Image,
    ImageFit,
    Tooltip,
    Column,
    Row,
    Divider,
)
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
                *[
                    RoundButton(
                        size=10 if star.type == StarType.minor else 22,
                        bgcolor=star.color,
                        left=star.coords[0],
                        top=star.coords[1],
                        tooltip=star.full_name,
                    )
                    for star in star_chart.get_stars()
                ]
            ],
            expand=True,
        )

    def setup_events(self):
        ...
