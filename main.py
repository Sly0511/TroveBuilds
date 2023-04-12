from flet import app, Page, SnackBar, Text, WEB_BROWSER, Theme, Column
from i18n import t

from models import Config
from utils.controls import TroveToolsAppBar
from utils.localization import LocalizationManager
from utils.logger import Logger
from views import GemSetView, GemView, MasteryView, StarView, HomeView, View404
from utils.objects import DiscordOAuth2
from dotenv import get_key


class TroveBuilds:
    def run(self):
        app(target=self.start, assets_dir="assets", view=WEB_BROWSER, port=13010)

    async def start(self, page: Page, restart=False, translate=False):
        if not restart:
            self.page = page
            page.login_provider = DiscordOAuth2(
                client_id=get_key(".env", "DISCORD_CLIENT"),
                client_secret=get_key(".env", "DISCORD_SECRET")
            )
            page.restart = self.restart
            page.logger = Logger("Trove Builds Core")
            # Load configurations
            self.load_configuration()
        # Setup localization
        self.setup_localization()
        # Build main window
        page.title = t("title")
        page.on_route_change = self.route_change
        page.on_keyboard_event = self.keyboard_shortcut
        page.theme = Theme(color_scheme_seed="red")
        page.theme_mode = await page.client_storage.get_async("theme") or "DARK"
        page.window_maximizable = True
        page.window_maximized = True
        page.window_resizable = False
        page.scroll = "auto"
        page.snack_bar = SnackBar(content=Text(""), bgcolor="green")
        if not hasattr(page, "all_views") or translate:
            page.all_views = [
                View404(page),
                HomeView(page),
                GemSetView(page),
                GemView(page),
                StarView(page),
                MasteryView(page),
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

    async def keyboard_shortcut(self, e):
        async def switch_tabs(e):
            views = self.page.all_views[2:]
            index = int(e.key) - 1
            if 0 <= index <= len(views) - 1:
                self.page.route = views[index].route
                await self.page.update_async()

        if (
            e.key.isnumeric()
            and not e.ctrl
            and not e.shift
            and e.alt
            and not e.meta
        ):
            await switch_tabs(e)

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
