from flet import (
    AppBar,
    Icon,
    IconButton,
    PopupMenuButton,
    PopupMenuItem,
    Divider,
    Row,
    CircleAvatar,
    Text,
    Container,
    VerticalDivider,
    Image,
    AlertDialog,
    TextButton,
    MainAxisAlignment
)
from flet_core.colors import SURFACE_VARIANT
from flet_core.icons import (
    LIGHT_MODE,
    DARK_MODE,
    LANGUAGE,
    HOME,
    NOW_WIDGETS_SHARP,
    PERSON,
    BUG_REPORT,
    HELP,
    LOGOUT,
)

from utils.localization import Locale


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
                IconButton(
                    data="theme_switcher",
                    icon=DARK_MODE
                    if self.page.theme_mode == "LIGHT"
                    else LIGHT_MODE,
                    on_click=self.change_theme,
                    tooltip="Change theme",
                ),
                PopupMenuButton(
                    content=Container(
                        Row(
                            controls=[
                                Icon(LANGUAGE),
                                Text(
                                    self.page.app_config.locale.name.replace("_", " ")
                                ),
                            ]
                        )
                    ),
                    items=[
                        PopupMenuItem(
                            data=loc,
                            text=loc.name.replace("_", " "),
                            on_click=self.change_locale,
                        )
                        for loc in Locale
                    ],
                    tooltip="Change language",
                ),
                VerticalDivider(),
                PopupMenuButton(
                    content=Container(
                        Row(controls=[Icon(NOW_WIDGETS_SHARP), Text("Apps")])
                    ),
                    items=[
                        PopupMenuItem(
                            data=view.route,
                            text=view.title.value,
                            icon=view.icon.name,
                            on_click=self.change_route,
                        )
                        for view in self.views
                        if view.route != "/" and self.page.route != view.route
                    ],
                    tooltip="Change tool",
                ),
                VerticalDivider(),
                (
                    PopupMenuButton(
                        content=Row(
                            controls=[
                                CircleAvatar(
                                    foreground_image_url=self.page.discord_user.avatar_url()
                                ),
                                Text(self.page.discord_user.display_name),
                            ]
                        ),
                        items=[
                            PopupMenuItem(
                                icon=LOGOUT, text="Logout", on_click=self.logout
                            ),
                        ],
                    )
                    if self.page.discord_user
                    else Container(
                        Row(
                            controls=[
                                IconButton(icon=PERSON, on_click=self.login),
                                Text("Login"),
                            ]
                        ),
                        on_click=self.login,
                    )
                ),
                PopupMenuButton(
                    data="other-buttons",
                    items=[
                        PopupMenuItem(
                            data="discord",
                            content=Row(
                                controls=[
                                    Image(
                                        (
                                            "assets/icons/brands/discord-mark-black.png"
                                            if self.page.theme_mode == "LIGHT"
                                            else "assets/icons/brands/discord-mark-white.png"
                                        ),
                                        width=19,
                                    ),
                                    Text("Discord"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        PopupMenuItem(
                            data="github",
                            content=Row(
                                controls=[
                                    Image(
                                        (
                                            "assets/icons/brands/github-mark-black.png"
                                            if self.page.theme_mode == "LIGHT"
                                            else "assets/icons/brands/github-mark-white.png"
                                        ),
                                        width=19,
                                    ),
                                    Text("Github"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        PopupMenuItem(
                            data="paypal",
                            content=Row(
                                controls=[
                                    Image(
                                        "assets/icons/brands/paypal-mark.png", width=19
                                    ),
                                    Text("Paypal"),
                                ]
                            ),
                            on_click=self.go_url,
                        ),
                        Divider(),
                        PopupMenuItem(
                            icon=BUG_REPORT,
                            data="discord",
                            text="Report a bug",
                            on_click=self.go_url,
                        ),
                        PopupMenuItem(icon=HELP, text="About", on_click=self.open_about),
                    ],
                    tooltip="Others",
                ),
            ]
        )
        actions.extend(kwargs.get("actions", []))
        super().__init__(
            leading_width=40, bgcolor=SURFACE_VARIANT, actions=actions, center_title=True, **kwargs
        )

    async def change_theme(self, _):
        self.page.theme_mode = "LIGHT" if self.page.theme_mode == "DARK" else "DARK"
        await self.page.client_storage.set_async("theme", self.page.theme_mode)
        for action in self.actions:
            if action.data == "theme_switcher":
                action.icon = (
                    DARK_MODE if self.page.theme_mode == "LIGHT" else LIGHT_MODE
                )
            if action.data == "other-buttons":
                for item in action.items:
                    if item.data in ["discord", "github"] and item.content is not None:
                        item.content.controls[0].src = (
                            f"assets/icons/brands/{item.data}-mark-black.png"
                            if self.page.theme_mode == "LIGHT"
                            else f"assets/icons/brands/{item.data}-mark-white.png"
                        )

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
            self.page.login_provider, on_open_authorization_url=self.open_blank_page
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
            "paypal": "https://www.paypal.com/paypalme/waterin",
        }
        await self.page.launch_url_async(urls[event.control.data])

    async def open_about(self, event):
        self.dlg = AlertDialog(
            modal=True,
            title=Text("About"),
            actions=[
                TextButton("Close", on_click=self.close_dlg),
            ],
            actions_alignment=MainAxisAlignment.END,
            content=Text("This application was made by Sly.\n\nI am coding this as an hobby with the goal of"
                         " achieving greater front-end building skills, at the same time I also improve code"
                         " making and organization skills\n\nI have the goal to not only build something"
                         " that is usable but mostly updatable with little effort or code knowledge"
                         " this however may be a challenge if newer updates come with changes on behavior of"
                         " previous content.\n\nI don't promise to keep this up to date forever, but as long as"
                         " I am around I should be able to.\n\nThanks for using my application. <3"),
            on_dismiss=lambda e: print("Modal dialog dismissed!"),
        )
        self.page.dialog = self.dlg
        self.dlg.open = True
        await self.page.update_async()

    async def close_dlg(self, e):
        self.dlg.open = False
        await self.page.update_async()
