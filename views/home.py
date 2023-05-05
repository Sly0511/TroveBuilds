from flet import View, Icon, Text, Column, Card, ResponsiveRow, Row
from flet_core.icons import HOME_SHARP
from controllers import HomeController


class HomeView(View):
    def __init__(self, page):
        self.title = Text("Home")
        self.icon = Icon(HOME_SHARP)
        ctrl = HomeController(page)
        super().__init__(
            route="/",
            controls=[
                ctrl.widgets
            ],
        )