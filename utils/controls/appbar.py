from flet import AppBar, IconButton, Icon, PopupMenuButton, PopupMenuItem

from flet_core.icons import WB_SUNNY_OUTLINED, LANGUAGE, HOME
from flet_core.colors import SURFACE_VARIANT
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
                IconButton(icon=WB_SUNNY_OUTLINED, on_click=self.change_theme),
                PopupMenuButton(
                    icon=LANGUAGE,
                    items=[
                        PopupMenuItem(
                            data=loc,
                            text=loc.name.replace("_", " "),
                            on_click=self.change_locale
                        )
                        for loc in Locale
                    ]
                ),
                PopupMenuButton(
                    items=[
                        PopupMenuItem(
                            data=view.route,
                            text=view.title.value,
                            icon=view.icon.name,
                            on_click=self.change_route
                        )
                        for view in self.views
                        if view.route != "/" and self.page.route != view.route
                    ]
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
        await self.page.update_async()

    async def change_locale(self, event):
        self.page.app_config.locale = event.control.data
        await self.page.restart(True)

    async def change_route(self, event):
        self.page.route = event.control.data
        await self.page.update_async()

    async def change_home(self, _):
        self.page.route = "/"
        await self.page.update_async()
