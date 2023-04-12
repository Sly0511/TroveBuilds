from flet import View, Icon, Text
from flet_core.icons import DIAMOND_SHARP
from i18n import t

from controllers import GemSetController


class GemSetView(View):
    def __init__(self, page):
        ctrl = GemSetController(page=page)
        self.title = Text(t("tabs.0"))
        self.icon = Icon(DIAMOND_SHARP)
        super().__init__(
            route="/gem_calculator",
            controls=[ctrl.gem_report, ctrl.general_controls, ctrl.gem_altar],
            scroll="auto",
        )
