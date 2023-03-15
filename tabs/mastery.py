from flet import Tab, Container, Column, Row, VerticalDivider
from i18n import t

from controllers import MasteryController


class Mastery(Tab):
    def __init__(self, page):
        ctrl = MasteryController(page=page)
        ctrl.container = Container(
            content=Column(
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
                ]
            ),
            expand=True,
            padding=10,
        )
        super().__init__(text=t("tabs.1"), content=ctrl.container)
