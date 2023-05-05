import flet as ft


class ScrollingFrame(ft.Container):
    def __init__(self, content, vertical_scrollbar_always_visible=True, **kwargs):
        super().__init__(**kwargs)

        self.expand = True

        first_dimension = ft.Column if vertical_scrollbar_always_visible else ft.Row
        second_dimension = ft.Row if vertical_scrollbar_always_visible else ft.Column

        self.content = first_dimension([other_direction := second_dimension([container := ft.Container()])])

        self.content.expand = True
        self.content.scroll = ft.ScrollMode.AUTO
        other_direction.scroll = ft.ScrollMode.AUTO

        container.content = content
