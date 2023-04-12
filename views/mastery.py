from flet import View, Icon, Row, VerticalDivider, Text
from flet_core.icons import DIAMOND_SHARP

from controllers import MasteryController
from utils.controls import TroveToolsAppBar


class MasteryView(View):
    def __init__(self, page):
        ctrl = MasteryController(page=page)
        self.title = Text("Mastery")
        self.icon = Icon(DIAMOND_SHARP)
        super().__init__(
            route="/mastery",
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
