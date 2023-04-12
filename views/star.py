from flet import View, Icon, Text, ElevatedButton
from flet_core.icons import STARS_SHARP

from controllers import StarChartController


class StarView(View):
    def __init__(self, page):
        ctrl = StarChartController(page=page)
        self.title = Text("Star Chart")
        self.icon = Icon(STARS_SHARP)
        super().__init__("/star_chart", controls=[ctrl.map, ElevatedButton("test")])
