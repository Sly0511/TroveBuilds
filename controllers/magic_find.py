import json

from flet import ResponsiveRow, Column, Switch, Slider, Card, Text

from models.objects import Controller


class MagicFindController(Controller):
    def setup_controls(self):
        if not hasattr(self, "interface"):
            self.interface = ResponsiveRow()
            self.control_values = {}
        self.magic_find_data = json.load(open("data/builds/magic_find.json"))
        buttons = []
        for source in self.magic_find_data:
            if source["name"] not in self.control_values:
                self.control_values[source["name"]] = True if source["type"] == "switch" else source["value"]
            if source["type"] == "switch":
                control = ResponsiveRow(
                    controls=[
                        Switch(
                            data=source["name"],
                            value=self.control_values[source["name"]],
                            col={"xxl": 3},
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
                            col={"xxl": 6}
                        )
                    ]
                )
            elif source["type"] == "slider":
                control = ResponsiveRow(
                    controls=[
                        Text(
                            (
                                source["name"] + " - " + str(
                                    source["value"]
                                    if not source["percentage"] else
                                    f"{round(source['value'], 2)}%"
                                )
                            )
                        ),
                        Slider(
                            data=source["name"],
                            value=self.control_values[source["name"]],
                            min=0,
                            max=source["value"],
                            divisions=int(source["value"] / 50),
                            label="{value}",
                            on_change_end=self.slider_stat
                        )
                    ]
                )
            else:
                continue
            control.col = {"xxl": 6}
            print(getattr(source, "divisions", None))
            buttons.append(control)
        result = 0
        for (_, v), source in zip(self.control_values.items(), self.magic_find_data):
            if isinstance(v, bool):
                v = source["value"] if v else 0
            if source["percentage"]:
                result *= 1 + v / 100
            else:
                result += v
        self.results = Card(
            content=ResponsiveRow(
                controls=[
                    Text("Total Magic Find", size=22, col={"xxl": 6}),
                    Text(round(result, 2), size=22, col={"xxl": 6})
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
        self.setup_controls()
        await self.page.update_async()

    async def slider_stat(self, event):
        self.control_values[event.control.data] = event.control.value
        self.setup_controls()
        await self.page.update_async()