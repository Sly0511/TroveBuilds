from flet import View, Icon, Text, Column
from flet_core.icons import TABLE_VIEW

from controllers import GemBuildsController


class GemBuildsView(View):
    def __init__(self, page):
        ctrl = GemBuildsController(page)
        self.title = Text("Gem Builds")
        self.icon = Icon(TABLE_VIEW)
        super().__init__(
            route="/gem_builds",
            controls=[Column(controls=[ctrl.character_data, ctrl.features, ctrl.data_table])],
        )
