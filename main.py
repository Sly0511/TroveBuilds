from flet import app, Page, Tabs, SnackBar, Text
from i18n import t

from models import Config
from tabs import Gems, Mastery
from utils.localization import LocalizationManager
from utils.logger import Logger


class TroveBuilds:
    def run(self):
        app(target=self.start)

    async def start(self, page: Page, restart=False):
        if not restart:
            self.page = page
            page.logger = Logger('Trove Builds Core')
            # Load configurations
            self.load_configuration()
        # Setup localization
        self.setup_localization()
        # Build main window
        page.title = t('title')
        page.window_maximizable = True
        page.window_maximized = True
        page.snack_bar = SnackBar(content=Text(""), bgcolor="green")
        # Build tab frames
        tabs = Tabs(
            tabs=[
                Gems(page),
                Mastery(page)
            ]
        )
        # Push UI elements into view
        await page.add_async(tabs)

    async def restart(self):
        await self.page.clean_async()
        await self.start(self.page, True)

    def load_configuration(self):
        self.page.app_config = Config()
        self.page.logger.debug("Configuration loaded -> " + repr(self.page.app_config))

    def setup_localization(self):
        LocalizationManager(self.page).update_all_translations()
        self.page.logger.info("Updated localization strings")


if __name__ == '__main__':
    AppObj = TroveBuilds()
    AppObj.run()
