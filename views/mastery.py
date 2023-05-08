from flet import View, Icon, Row, VerticalDivider, Text
from flet_core.icons import MENU_BOOK_SHARP

from controllers import MasteryController


class MasteryView(View):
    route = "/mastery"
    title = Text("Mastery")
    icon = MENU_BOOK_SHARP

    def __init__(self, page):
        ctrl = MasteryController(page=page)
        super().__init__(
            route=self.route,
            controls=[
                ctrl.points_input,
                ctrl.level_input,
                Row(
                    controls=[
                        ctrl.mastery_buffs,
                        VerticalDivider(),
                        ctrl.geode_buffs,
                    ],
                    vertical_alignment="start",
                ),
            ],
        )
