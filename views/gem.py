from flet import View, Text, Icon
from flet_core.icons import SCIENCE_SHARP
from i18n import t

from controllers import GemController
from utils.controls import TroveToolsAppBar


class GemView(View):
    def __init__(self, page):
        ctrl = GemController(page=page)
        self.title = Text(t("tabs.3"))
        self.icon = Icon(SCIENCE_SHARP)
        super().__init__(
            route="/gem_simulator",
            controls=[ctrl.header_row],
            scroll="auto"
        )
