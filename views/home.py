from flet import View, Icon, Text, Column
from flet_core.icons import HOME_SHARP

from utils.controls import TroveToolsAppBar


class HomeView(View):
    def __init__(self, page):
        self.title = Text("Home")
        self.icon = Icon(HOME_SHARP)
        super().__init__(
            route="/",
            controls=[
                Column(
                    controls=[
                        Text("Welcome")
                    ]
                )
            ]
        )
