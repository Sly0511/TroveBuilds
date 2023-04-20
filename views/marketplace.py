from flet import View, Icon, Text
from flet_core.icons import COMMENT_BANK

from controllers import MarketplaceController


class MarketplaceView(View):
    def __init__(self, page):
        ctrl = MarketplaceController(page)
        self.title = Text('Marketplace')
        self.icon = Icon(COMMENT_BANK)
        super().__init__(
            route="/marketplace",
            controls=[
                ctrl.page
            ]
        )