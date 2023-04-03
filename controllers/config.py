from flet import ElevatedButton, Stack, Column, Dropdown, dropdown, Text

# from i18n import t

from models.objects import Controller
from models.config import Locale
import asyncio


class ConfigController(Controller):
    def setup_controls(self):
        self.settings = Column(
            controls=[
                Column(
                    controls=[
                        Dropdown(
                            value=self.page.app_config.locale.value,
                            options=[
                                dropdown.Option(key=loc.value, text=loc.name.replace("_", " "))
                                for loc in Locale
                            ],
                            label="Language",
                            on_change=self.on_language_change,
                        ),
                    ]
                ),
                Column(
                    controls=[
                        Text("This application was developed by Sly#0511.\nIt's use is free and")
                    ]
                )
            ],
            expand=True,
            spacing=400
        )

    def setup_events(self):
        ...

    async def on_language_change(self, event):
        lang = Locale(event.control.value)
        self.page.app_config.locale = lang
        self.page.snack_bar.content.value = "Switched to " + lang.name.replace("_", " ")
        self.page.snack_bar.open = True
        for control in self.page.controls:
            control.disabled = True
        await self.page.update_async()
        await asyncio.sleep(1.5)
        await self.page.restart()
