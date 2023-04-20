import asyncio

from dotenv import get_key
from flet import app, Page, SnackBar, Text, WEB_BROWSER, Theme, Column
from flet.security import encrypt, decrypt
from httpx import HTTPStatusError
from i18n import t

from models import Config
from models.objects.discord_user import DiscordUser
from utils.controls import TroveToolsAppBar
from utils.localization import LocalizationManager, Locale
from utils.logger import Logger
from utils.objects import DiscordOAuth2
from datetime import datetime, timedelta
from utils import tasks
from views import GemSetView, GemView, MasteryView, StarView, HomeView, GemBuildsView, MarketplaceView, View404


class TroveBuilds:
    def run(self):
        app(target=self.start, assets_dir="assets", view=WEB_BROWSER, port=13010)

    async def start(self, page: Page, restart=False, translate=False):
        if not restart:
            self.page = page
            page.clock = Text("Trove Time")
            page.login_provider = DiscordOAuth2(
                client_id=get_key(".env", "DISCORD_CLIENT"),
                client_secret=get_key(".env", "DISCORD_SECRET")
            )
            page.restart = self.restart
            page.logger = Logger("Trove Builds Core")
            # Load configurations
            await self.load_configuration()
        # Setup localization
        self.setup_localization()
        # Build main window
        page.title = t("title")
        # Setup Events
        page.on_login = self.on_login
        page.on_logout = self.on_logout
        page.on_route_change = self.route_change
        page.on_keyboard_event = self.keyboard_shortcut
        # Setup app interface data
        page.theme = Theme(color_scheme_seed="red")
        page.theme_mode = await page.client_storage.get_async("theme") or "DARK"
        page.window_maximizable = True
        page.window_maximized = True
        page.window_resizable = False
        page.padding = 0
        page.scroll = "auto"
        page.snack_bar = SnackBar(content=Text(""), bgcolor="green")
        await self.check_login()
        if not hasattr(page, "all_views") or translate:
            page.all_views = [
                View404(page),
                HomeView(page),
                GemSetView(page),
                GemView(page),
                StarView(page),
                MasteryView(page),
                GemBuildsView(page),
                MarketplaceView(page)
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
        if not self.update_clock.is_running():
            self.update_clock.start()

    async def check_login(self):
        self.page.secret_key = get_key(".env", "APP_SECRET")
        self.page.discord_user = None
        if self.page.auth is None and await self.page.client_storage.contains_key_async("login"):
            try:
                encrypted_token = await self.page.client_storage.get_async("login")
                await self.page.login_async(
                    self.page.login_provider,
                    saved_token=decrypt(encrypted_token, self.page.secret_key)
                )
                return
            except HTTPStatusError:
                await self.page.client_storage.remove_async("login")
                await self.page.logout_async()
                self.page.logger.debug("User logged out: Invalidated token")
        if self.page.auth is None:
            return
        self.page.discord_user = DiscordUser(**self.page.auth.user)
        encrypted_token = encrypt(self.page.auth.token.to_json(), self.page.secret_key)
        await self.page.client_storage.set_async("login", encrypted_token)

    async def on_login(self, event):
        while self.page.auth is None:
            await asyncio.sleep(1)
        self.page.discord_user = DiscordUser(**self.page.auth.user)
        self.page.logger.debug(f"User Login: [{self.page.discord_user.id}] {self.page.discord_user.display_name}")
        await self.restart()

    async def on_logout(self, event):
        self.page.logger.debug(f"User Logout: [{self.page.discord_user.id}] {self.page.discord_user.display_name}")
        while self.page.auth is not None:
            await asyncio.sleep(1)
        await self.restart()

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

    async def load_configuration(self):
        self.page.app_config = Config()
        if await self.page.client_storage.contains_key_async("locale"):
            try:
                loc = Locale(await self.page.client_storage.get_async("locale"))
                self.page.app_config.locale = loc
            except ValueError:
                await self.page.client_storage.set_async("locale", Locale.American_English.value)
        else:
            await self.page.client_storage.set_async("locale", Locale.American_English.value)
        self.page.logger.debug("Configuration loaded -> " + repr(self.page.app_config))

    def setup_localization(self):
        LocalizationManager(self.page).update_all_translations()
        self.page.logger.info("Updated localization strings")

    @tasks.loop(seconds=1)
    async def update_clock(self):
        self.page.clock.value = (datetime.utcnow() - timedelta(hours=11)).strftime("Trove Time: %Y-%m-%d\t\t%H:%M:%S")
        await self.page.clock.update_async()


if __name__ == "__main__":
    AppObj = TroveBuilds()
    AppObj.run()
