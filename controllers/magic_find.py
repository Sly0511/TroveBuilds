import json

from flet import ResponsiveRow, Column, Switch, Slider, Card, Text, TextField

from models.objects import Controller
from utils.star_chart import get_star_chart
from utils.controls import NumberField
from utils.functions import long_throttle


class MagicFindController(Controller):
    def setup_controls(self):
        if not hasattr(self, "interface"):
            self.star_chart = get_star_chart()
            self.interface = ResponsiveRow()
            self.control_values = {
                "mastery": 250,
                "Patron": True
            }
        self.magic_find_data = json.load(open("data/builds/magic_find.json"))
        buttons = [
            ResponsiveRow(
                controls=[
                    NumberField(
                        data="mastery",
                        type=int,
                        value=self.control_values["mastery"] + 500,
                        min=500,
                        max=1000,
                        on_change=self.mastery_stat,
                        label="Mastery Level",
                        col=6
                    )
                ]
            )
        ]
        for source in self.magic_find_data:
            if source["name"] not in self.control_values:
                self.control_values[source["name"]] = True if source["type"] == "switch" else source["value"]
            if source["type"] == "switch":
                control = ResponsiveRow(
                    controls=[
                        Switch(
                            data=source["name"],
                            value=self.control_values[source["name"]],
                            col=3,
                            on_change=self.switch_stat
                        ),
                        Text(
                            (
                                source["name"] + " - " + str(
                                    source["value"]
                                    if not source["percentage"] else
                                    f"{round(source['value'], 2)}%"
                                )
                            ),
                            col=9
                        )
                    ]
                )
            elif source["type"] == "slider":
                control = ResponsiveRow(
                    controls=[
                        NumberField(
                            data=source["name"],
                            type=int,
                            value=self.control_values[source["name"]],
                            min=0,
                            max=source["value"],
                            step=50,
                            on_change=self.slider_stat,
                            label=source["name"],
                        )
                    ]
                )
            else:
                continue
            control.col = {"xxl": 6}
            buttons.append(control)
        buttons.append(
            ResponsiveRow(
                controls=[
                    Switch(
                        data="Patron",
                        value=self.control_values["Patron"],
                        col=3,
                        on_change=self.switch_stat
                    ),
                    Text(
                        "Patron - 200%",
                        col=9
                    )
                ],
                col=6
            )
        )
        buttons.append(
            TextField(
                hint_text="Star Chart Build ID | \"none\" to remove",
                on_change=self.set_star_chart_build,
                text_size=14,
                height=58,
                col={"xxl": 6}
            )
        )
        buttons.append(
            Column(
                controls=[
                    Text(f"{k}: {v[0]}" + ("%" if v[1] else ""))
                    for k, v in self.star_chart.activated_select_stats("Magic Find").items()
                ]
            )
        )
        result = 0
        result += self.control_values["mastery"]
        for k, v in self.star_chart.activated_select_stats("Magic Find").items():
            if not v[1]:
                result += v[0]
        bonus = 0
        for (_, v), source in zip(list(self.control_values.items())[2:], self.magic_find_data):
            if isinstance(v, bool):
                v = source["value"] if v else 0
            if not source["percentage"]:
                result += v
            else:
                bonus += v
        for k, v in self.star_chart.activated_select_stats("Magic Find").items():
            if v[1]:
                bonus += v[0]
        result *= 1 + bonus / 100
        result *= 2 if self.control_values["Patron"] else 1
        self.results = Card(
            content=ResponsiveRow(
                controls=[
                    Text("Total Magic Find", size=22, col=6),
                    Text(str(round(result, 2)), size=22, col=6)
                ]
            ),
            col={"xxl": 3}
        )
        self.interface.controls = [
            Card(
                content=Column(
                    controls=[
                        ResponsiveRow(
                            controls=buttons
                        )
                    ]
                ),
                col={"xxl": 5}
            ),
            self.results
        ]

    def setup_events(self):
        ...

    async def switch_stat(self, event):
        self.control_values[event.control.data] = event.control.value
        self.page.snack_bar.content.value = f"Updated {event.control.data}"
        self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    async def slider_stat(self, event):
        self.control_values[event.control.data] = int(event.control.value)
        self.page.snack_bar.content.value = f"Updated {event.control.data}"
        self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    async def mastery_stat(self, event):
        self.control_values[event.control.data] = int(event.control.value) - 500
        self.page.snack_bar.content.value = f"Updated {event.control.data}"
        self.page.snack_bar.open = True
        self.setup_controls()
        await self.page.update_async()

    async def set_star_chart_build(self, event):
        build_id = event.control.value.strip().split("-")[-1].strip()
        self.star_chart = get_star_chart()
        if build_id == "none":
            self.setup_controls()
            await self.page.update_async()
            return
        if await self.star_chart.from_string(build_id):
            self.page.snack_bar.content.value = f"Loaded build with id {build_id}"
            self.page.snack_bar.open = True
            self.setup_controls()
            await self.page.update_async()
