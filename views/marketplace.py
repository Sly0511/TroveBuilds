from flet import View, Icon, Text
from flet_core.icons import COMMENT_BANK

from controllers import MarketplaceController


class MarketplaceView(View):
    route = "/marketplace"
    title = Text("[BETA] Marketplace")
    icon = Icon(COMMENT_BANK)

    def __init__(self, page):
        ctrl = MarketplaceController(page)
        super().__init__(route=self.route, controls=[ctrl.main])
