from flet import Tab, Container, Column
from i18n import t
import flet_core.icons as ico

from controllers import GemController


class Gem(Tab):
    def __init__(self, page):
        ctrl = GemController(page=page)
        ctrl.container = Container(
            content=Column(
                controls=[
                    ctrl.header_row
                ]
            ),
            padding=10
        )
        super().__init__(
            text=t("tabs.3"), content=ctrl.container, icon=ico.DIAMOND_SHARP
        )
