from flet import Tab, Container, Column
from controllers import GemsController
from i18n import t


class Gems(Tab):
    def __init__(self, page):
        ctrl = GemsController(page=page)
        ctrl.container = Container(
            content=Column(
                controls=[
                    ctrl.gem_report,
                    ctrl.general_controls,
                    ctrl.gem_holder,
                    ctrl.gem_editor
                ],
                scroll="auto"
            )
        )
        super().__init__(
            text=t('tabs.0'),
            content=ctrl.container
        )