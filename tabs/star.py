from flet import Tab, Container, Column
from i18n import t
import flet_core.icons as ico

from controllers import StarChartController


class StarChart(Tab):
    def __init__(self, page):
        ctrl = StarChartController(page=page)
        ctrl.container = Container(content=ctrl.map)
        super().__init__(text=t("tabs.2"), content=ctrl.container, icon=ico.STARS_SHARP)
