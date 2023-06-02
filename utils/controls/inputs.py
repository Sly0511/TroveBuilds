from flet import TextField, TextStyle
import re
from typing import Optional, Union
from utils.functions import long_throttle


int_regex = re.compile("^-?\d+$")
float_regex = re.compile("^-?\d+((?:\.|\,)\d*)?$")


class NumberField(TextField):
    def __init__(
            self,
            type=float,
            min: Optional[Union[int, float]] = None,
            max: Optional[Union[int, float]] = None,
            step: Optional[int] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.ensured_type = type
        number_value = kwargs.get('value', None)
        self.number_value = self.ensured_type(number_value) if number_value is not None else None
        self.min = min
        self.max = max
        self.step = step

    @property
    def on_change(self):
        return self._get_event_handler("change")

    @on_change.setter
    def on_change(self, handler):
        @long_throttle
        async def verify_value(event):
            event.control.border_color = None
            event.control.label_style = None
            if event.control.ensured_type is int:
                regex = int_regex
            elif event.control.ensured_type is float:
                regex = float_regex
            else:
                raise TypeError("ensured_type must be of type float or int.")
            if not regex.match(event.control.value):
                event.control.border_color = "red"
                event.control.label_style = TextStyle(color="red")
                return await event.control.update_async()
            event.control.number_value = event.control.ensured_type(event.control.value)
            if (minimum := event.control.min) is not None:
                if event.control.number_value < minimum:
                    event.control.number_value = self.min
                    event.control.value = str(event.control.number_value)
            if (maximum := event.control.max) is not None:
                if event.control.number_value > maximum:
                    event.control.number_value = self.max
                    event.control.value = str(event.control.number_value)
            if event.control.step is not None:
                mult, rest = divmod(event.control.number_value, event.control.step)
                event.control.number_value = mult * event.control.step
                if rest:
                    event.control.number_value += event.control.step
                event.control.value = str(event.control.number_value)
            await event.control.update_async()
            await handler(event)
        self._add_event_handler("change", verify_value)
        if handler is not None:
            self._set_attr("onchange", True)
        else:
            self._set_attr("onchange", None)
