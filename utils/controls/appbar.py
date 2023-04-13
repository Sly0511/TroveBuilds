from flet import AppBar, Icon, IconButton, PopupMenuButton, PopupMenuItem, Divider, Row, CircleAvatar, Text, Container


from flet_core.icons import WB_SUNNY_OUTLINED, WB_SUNNY, LANGUAGE, HOME, NOW_WIDGETS_SHARP, PERSON, BUG_REPORT, HELP, LOGOUT
from flet_core.colors import SURFACE_VARIANT
from utils.localization import Locale
import asyncio


class TroveToolsAppBar(AppBar):
    def __init__(self, **kwargs):
        self.views = kwargs["views"]
        self.page = kwargs["page"]
        del kwargs["views"]
        del kwargs["page"]
        actions = []
        if self.page.route != "/":
            actions.append(IconButton(icon=HOME, on_click=self.change_home))
        actions.extend(
            [
                IconButton(icon=WB_SUNNY_OUTLINED if self.page.theme_mode == "LIGHT" else WB_SUNNY, on_click=self.change_theme, tooltip="Change theme"),
                PopupMenuButton(
                    content=Container(
                        Row(
                            controls=[
                                Icon(LANGUAGE),
                                Text(self.page.app_config.locale.name.replace("_", " "))
                            ]
                        )
                    ),
                    items=[
                        PopupMenuItem(
                            data=loc,
                            text=loc.name.replace("_", " "),
                            on_click=self.change_locale
                        )
                        for loc in Locale
                    ],
                    tooltip="Change language"
                ),
                PopupMenuButton(
                    content=Container(
                        Row(
                            controls=[
                                Icon(NOW_WIDGETS_SHARP),
                                Text("Apps")
                            ]
                        )
                    ),
                    items=[
                        PopupMenuItem(
                            data=view.route,
                            text=view.title.value,
                            icon=view.icon.name,
                            on_click=self.change_route
                        )
                        for view in self.views
                        if view.route != "/" and self.page.route != view.route
                    ],
                    tooltip="Change tool"
                ),
                (
                    PopupMenuButton(
                        content=Row(
                            controls=[
                                CircleAvatar(foreground_image_url=self.page.discord_user.avatar_url()),
                                Text(self.page.discord_user.display_name)
                            ]
                        ),
                        items=[
                            PopupMenuItem(icon=LOGOUT, text="Logout", on_click=self.logout),
                        ]
                    )
                    if self.page.discord_user else
                    Container(
                        Row(
                            controls=[
                                IconButton(
                                    icon=PERSON,
                                    on_click=self.login
                                ),
                                Text("Login")
                            ]
                        ),
                        on_click=self.login
                    )
                ),
                PopupMenuButton(
                    items=[
                        PopupMenuItem(data="discord", text="Discord", on_click=self.go_url),
                        PopupMenuItem(data="github", text="Github", on_click=self.go_url),
                        PopupMenuItem(data="paypal", text="Paypal", on_click=self.go_url),
                        Divider(),
                        PopupMenuItem(icon=BUG_REPORT, data="discord", text="Report a bug", on_click=self.go_url),
                        PopupMenuItem(icon=HELP, text="About")
                    ],
                    tooltip="Others"
                )
            ]
        )
        actions.extend(kwargs.get("actions", []))
        super().__init__(
            leading_width=40, bgcolor=SURFACE_VARIANT, actions=actions, **kwargs
        )

    async def change_theme(self, _):
        self.page.theme_mode = (
            "LIGHT" if self.page.theme_mode == "DARK" else "DARK"
        )
        await self.page.client_storage.set_async("theme", self.page.theme_mode)
        await self.page.update_async()

    async def change_locale(self, event):
        self.page.app_config.locale = event.control.data
        await self.page.client_storage.set_async("locale", event.control.data.value)
        await self.page.restart(True)

    async def change_route(self, event):
        self.page.route = event.control.data
        await self.page.update_async()

    async def change_home(self, _):
        self.page.route = "/"
        await self.page.update_async()

    async def login(self, _):
        await self.page.login_async(
            self.page.login_provider,
            on_open_authorization_url=self.open_blank_page
        )

    async def logout(self, _):
        await self.page.client_storage.remove_async("login")
        await self.page.logout_async()

    async def open_blank_page(self, url):
        await self.page.launch_url_async(url, web_window_name="_blank")

    async def go_url(self, event):
        urls = {
            "discord": "https://discord.gg/duuFEsFWk5",
            "github": "https://github.com/Sly0511/TroveBuilds",
            "paypal": "https://www.paypal.com/paypalme/waterin"
        }
        await self.page.launch_url_async(urls[event.control.data])
