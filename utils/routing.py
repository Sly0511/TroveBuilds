from flet import Page, View, AppBar
from utils.functions import get_attr
from typing import Type


class Routing:
    def __init__(
        self,
        page: Page,
        views: list[Type[View]],
        not_found: Type[View] = None,
        is_async: bool = False,
    ):
        self.page = page
        self.views = views
        self.not_found = not_found
        if not is_async:
            self.page.on_route_change = self.handle_route_change
        else:
            self.page.on_route_change = self.handle_route_change_async

    def handle_route_change(self, event):
        view = self.get_view(event)
        self.change_view(view)

    async def handle_route_change_async(self, event):
        view = self.get_view(event)
        await self.change_view_async(view)

    def get_view(self, event):
        view = get_attr(self.views, route=event.route)
        if view is None:
            view = self.not_found
        return view(self.page)

    async def change_view(self, view: Type[View]):
        self.page.controls = view.controls
        self.page.update()

    async def change_view_async(self, view: Type[View]):
        self.page.controls = view.controls
        await self.page.update_async()
