from flet import ElevatedButton, Stack, Container

# from i18n import t

from models.objects import Controller


class StarChartController(Controller):
    def setup_controls(self):
        self.map = Stack(
            controls=[ElevatedButton(bgcolor="black")],
        )

    def setup_events(self):
        ...
