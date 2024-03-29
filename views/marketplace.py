from flet import View, Text
from flet_core.icons import COMMENT_BANK

from controllers import MarketplaceController


class MarketplaceView(View):
    route = "/marketplace"
    title = Text("[BETA] Marketplace")
    icon = COMMENT_BANK

    def __init__(self, page):
        ctrl = MarketplaceController(page)
        page.appbar.leading.controls[0].name = self.icon
        super().__init__(route=self.route, controls=[ctrl.main])
