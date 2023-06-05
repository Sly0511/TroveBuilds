from flet import View, Text
from flet_core.icons import HOME_SHARP

from controllers import HomeController


class HomeView(View):
    route = "/"
    title = Text("Home")
    icon = HOME_SHARP

    def __init__(self, page):
        ctrl = HomeController(page)
        super().__init__(
            route=self.route,
            controls=[ctrl.widgets],
        )
