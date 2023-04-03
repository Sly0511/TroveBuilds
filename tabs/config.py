from flet import Tab, Container
import flet_core.icons as ico

from controllers import ConfigController


class Configurations(Tab):
    def __init__(self, page):
        ctrl = ConfigController(page=page)
        ctrl.container = Container(
            content=ctrl.settings,
        )
        super().__init__(content=ctrl.container, icon=ico.SETTINGS_SHARP)
