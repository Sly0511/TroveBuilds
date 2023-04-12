from flet import View, Icon, Column, Text
from flet_core.icons import QUESTION_MARK


class View404(View):
    def __init__(self, page):
        self.title = Text("404 - Not Found")
        self.icon = Icon(QUESTION_MARK)
        super().__init__(
            route="/404",
            controls=[
                Column(
                    controls=[
                        Text("404 - Page not found", size=50),
                        Text("Looks like you are lost", size=50),
                    ]
                ),
            ],
        )
