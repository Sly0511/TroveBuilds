from flet import View, Icon, Text
from flet_core.icons import DIAMOND_SHARP
from i18n import t

from controllers import GemSetController


class GemSetView(View):
    route = "/gem_calculator"
    title = Text(t("tabs.0"))
    icon = Icon(DIAMOND_SHARP)

    def __init__(self, page):
        ctrl = GemSetController(page=page)
        super().__init__(
            route=self.route,
            controls=[ctrl.gem_report, ctrl.general_controls, ctrl.gem_altar],
            scroll="auto",
        )
