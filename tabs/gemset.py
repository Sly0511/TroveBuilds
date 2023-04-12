from flet import Tab, Container, Column
from i18n import t
import flet_core.icons as ico

from controllers import GemSetController


class GemSet(Tab):
    def __init__(self, page):
        ctrl = GemSetController(page=page)
        ctrl.container = Container(
            content=Column(
                controls=[ctrl.gem_report, ctrl.general_controls, ctrl.gem_altar]
            )
        )
        super().__init__(
            text=t("tabs.0"), content=ctrl.container, icon=ico.DIAMOND_SHARP
        )
