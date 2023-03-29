from flet import Tab, Container, Column
from i18n import t

from controllers import GemsController


class Gems(Tab):
    def __init__(self, page):
        ctrl = GemsController(page=page)
        ctrl.container = Container(
            content=Column(
                controls=[
                    ctrl.gem_report,
                    ctrl.general_controls,
                    ctrl.gem_holder,
                    ctrl.gem_editor,
                ]
            )
        )
        super().__init__(text=t("tabs.0"), content=ctrl.container)
