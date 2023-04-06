from flet import app, Page, Tabs, SnackBar, Text, WEB_BROWSER
from i18n import t

from models import Config
from tabs import Configurations, Gems, Mastery, StarChart
from utils.localization import LocalizationManager
from utils.logger import Logger


class TroveBuilds:
    def run(self):
        app(target=self.start, assets_dir="assets", view=WEB_BROWSER, port=13010)

    async def start(self, page: Page, restart=False):
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
        page.window_maximizable = True
        page.window_maximized = True
        page.window_resizable = False
        page.scroll = "auto"
        page.snack_bar = SnackBar(content=Text(""), bgcolor="green")
        # Build tab frames
        self.page.tabs = Tabs(
            tabs=[Configurations(page), Gems(page), StarChart(page), Mastery(page)],
            selected_index=self.page.tabs.selected_index if hasattr(self.page, "tabs") else 1,
        )
        # Push UI elements into view
        await page.add_async(self.page.tabs)

    async def restart(self):
        await self.page.clean_async()
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
