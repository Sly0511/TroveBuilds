from flet import View, Icon, Text
from flet_core.icons import STARS_SHARP

from controllers import StarChartController


class StarView(View):
    def __init__(self, page):
        ctrl = StarChartController(page=page)
        self.title = Text("[WIP] Star Chart")
        self.icon = Icon(STARS_SHARP)
        super().__init__("/star_chart", controls=[ctrl.map], spacing=0, padding=0)
