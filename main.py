from flet import app, Page, Tabs, SnackBar, Text, WEB_BROWSER, Theme, View, Column
from i18n import t
import asyncio

from models import Config
from tabs import Configurations, Gem, GemSet, Mastery, StarChart, Login
from views import GemSetView, GemView, MasteryView, StarView, HomeView, View404
from utils.localization import LocalizationManager
from utils.logger import Logger
from utils.controls import TroveToolsAppBar


class TroveBuilds:
    def run(self):
        app(target=self.start, assets_dir="assets", view=WEB_BROWSER, port=13010)

    async def start(self, page: Page, restart=False, translate=False):
        if not restart:
            self.page = page
            self.page.restart = self.restart
            page.logger = Logger("Trove Builds Core")
            # Load configurations
            self.load_configuration()
        # Setup localization
        self.setup_localization()
        # Build main window
        page.title = t("title")
        page.on_route_change = self.route_change
        page.theme = Theme(color_scheme_seed="red")
        page.theme_mode = "DARK"
        page.window_maximizable = True
        page.window_maximized = True
        page.window_resizable = False
        page.scroll = "auto"
        page.on_keyboard_event = ...
        page.snack_bar = SnackBar(content=Text(""), bgcolor="green")
        if not hasattr(page, "all_views") or translate:
            page.all_views = [
                View404(page),
                HomeView(page),
                GemSetView(page),
                MasteryView(page),
                StarView(page),
                GemView(page),
            ]
        for view in page.all_views:
            view.appbar = TroveToolsAppBar(
                leading=view.icon, title=view.title, views=page.all_views[1:], page=page
            )
        # Push UI elements into view
        await page.clean_async()
        view = page.all_views[0]
        for v in page.all_views[1:]:
            if v.route == page.route:
                view = v
        page.appbar = view.appbar
        await page.add_async(Column(controls=view.controls))

    async def restart(self, translate=False):
        await self.start(self.page, True, translate)

    async def route_change(self, route):
        await self.start(self.page, True)

    def load_configuration(self):
        self.page.app_config = Config()
        self.page.logger.debug("Configuration loaded -> " + repr(self.page.app_config))

    def setup_localization(self):
        LocalizationManager(self.page).update_all_translations()
        self.page.logger.info("Updated localization strings")


if __name__ == "__main__":
    AppObj = TroveBuilds()
    AppObj.run()
