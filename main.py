import asyncio
from datetime import datetime, timedelta

from beanie import init_beanie
from dotenv import get_key
from flet import app, Page, SnackBar, Text, WEB_BROWSER, Theme, Row, Icon
from flet.security import encrypt, decrypt
from httpx import HTTPStatusError
from i18n import t
from motor.motor_asyncio import AsyncIOMotorClient

from models import Config
from models.objects import StarBuild, BuildConfig
from models.objects.discord_user import DiscordUser
from models.objects.marketplace import Listing, Item
from models.objects.user import User
from utils import tasks
from utils.controls import TroveToolsAppBar
from utils.localization import LocalizationManager, Locale
from utils.logger import Logger
from utils.objects import DiscordOAuth2
from utils.routing import Routing
from views import (
    GemSetView,
    GemView,
    MasteryView,
    StarView,
    HomeView,
    GemBuildsView,
    View404,
    MagicFindView,
)


class Constants:
    trove_items: list = []
    database_client: AsyncIOMotorClient = AsyncIOMotorClient()
    database = None
    discord_user: DiscordUser = None
    market_log_webhook: str = None
    app_config: Config = Config()
    secret_key: str = get_key(".env", "APP_SECRET")


class TroveBuilds:
    def run(self):
        app(target=self.start, assets_dir="assets", view=WEB_BROWSER, port=13010)

    async def start(self, page: Page, restart=False, translate=False):
        if not restart:
            self.page = page
            page.constants = Constants()
            page.constants.database = await init_beanie(
                page.constants.database_client.trovetools,
                document_models=[User, Listing, Item, StarBuild, BuildConfig],
            )
            page.clock = Text(
                (datetime.utcnow() - timedelta(hours=11)).strftime("%a, %b %d\t\t%H:%M")
            )
            page.login_provider = DiscordOAuth2(
                client_id=get_key(".env", "DISCORD_CLIENT"),
                client_secret=get_key(".env", "DISCORD_SECRET"),
            )
            page.restart = self.restart
            page.open_blank_page = self.open_blank_page
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
        page.on_keyboard_event = self.keyboard_shortcut
        # Setup app interface data
        page.theme = Theme()
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
                HomeView,
                GemSetView,
                GemView,
                StarView,
                MasteryView,
                MagicFindView,
                GemBuildsView,
            ]
        page.appbar = TroveToolsAppBar(
            leading=Row(controls=[Icon("Star"), page.clock]),
            views=page.all_views[1:],
            page=page,
        )
        # Setup routing
        Routing(page, page.all_views, not_found=View404, is_async=True)
        await page.go_async(self.page.route)
        if not self.update_clock.is_running():
            self.update_clock.start()

    async def check_login(self):
        if (
            self.page.auth is None
            and (encrypted_token := await self.page.client_storage.get_async("login"))
            is not None
        ):
            try:

                await self.page.login_async(
                    self.page.login_provider,
                    saved_token=decrypt(
                        encrypted_token, self.page.constants.secret_key
                    ),
                )
                return
            except HTTPStatusError:
                await self.page.client_storage.remove_async("login")
                await self.page.logout_async()
                self.page.logger.debug("User logged out: Invalidated token")
        if self.page.auth is None or self.page.auth.user is None:
            return
        self.page.constants.discord_user = DiscordUser(**self.page.auth.user)
        encrypted_token = encrypt(
            self.page.auth.token.to_json(), self.page.constants.secret_key
        )
        await self.page.client_storage.set_async("login", encrypted_token)

    async def on_login(self, event):
        while self.page.auth is None:
            await asyncio.sleep(1)
        self.page.constants.discord_user = DiscordUser(**self.page.auth.user)
        if (
            user := await User.find_one(
                User.discord_id == int(self.page.constants.discord_user.id)
            )
        ) is None:
            user = User(discord_id=int(self.page.constants.discord_user.id))
            await user.save()
        self.page.logger.debug(
            f"User Login: [{self.page.constants.discord_user.id}] {self.page.constants.discord_user.display_name}"
        )
        if user.blocked:
            await self.page.logout_async()
        await self.restart()

    async def on_logout(self, event):
        self.page.logger.debug(
            f"User Logout: [{self.page.constants.discord_user.id}] {self.page.constants.discord_user.display_name}"
        )
        while self.page.auth is not None:
            await asyncio.sleep(1)
            self.page.constants.discord_user = None
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

        if e.key.isnumeric() and not e.ctrl and not e.shift and e.alt and not e.meta:
            await switch_tabs(e)

    async def load_configuration(self):
        if (
            locale_data := await self.page.client_storage.get_async("locale")
            is not None
        ):
            try:
                loc = Locale(locale_data)
                self.page.constants.app_config.locale = loc
            except ValueError:
                await self.page.client_storage.set_async(
                    "locale", Locale.American_English.value
                )
        else:
            await self.page.client_storage.set_async(
                "locale", Locale.American_English.value
            )
        self.page.logger.debug(
            "Configuration loaded -> " + repr(self.page.constants.app_config)
        )

    def setup_localization(self):
        LocalizationManager(self.page).update_all_translations()
        self.page.logger.info("Updated localization strings")

    async def open_blank_page(self, url):
        await self.page.launch_url_async(url, web_window_name="_blank")

    @tasks.loop(seconds=60)
    async def update_clock(self):
        self.page.clock.value = (datetime.utcnow() - timedelta(hours=11)).strftime(
            "%a, %b %d\t\t%H:%M"
        )
        try:
            await self.page.clock.update_async()
        except Exception:
            ...

    @update_clock.before_loop
    async def sync_clock(self):
        now = datetime.utcnow()
        await asyncio.sleep(60 - now.second)


if __name__ == "__main__":
    AppObj = TroveBuilds()
    AppObj.run()
