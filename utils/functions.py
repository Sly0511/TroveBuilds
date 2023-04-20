import asyncio
import datetime
from random import randint

__all__ = ["throttle", "split_boosts"]


def throttle(actual_handler, data={}, delay=0.5):
    """Throttles a function from running using python's memory gimmicks.

    This solves a race condition for searches to the database and loading data into the UI.
    Now you see Python will use that dict object for all the functions that run this decorator.
    Which means all delay times are shared, not ideal but saves the time of setting up the variables.
    Ideally I would not rely on this Python gimmick as it might change in the future.
    If for some reason this stopped working, check if python still defines and uses same dict object upon...
    ...function definition.

    I did not get a degree, don't sue me"""

    async def wrapper(e, i=None):
        """Simple filter for queries that shouldn't run."""

        data["last_change"] = datetime.datetime.utcnow().timestamp()
        await asyncio.sleep(delay)
        if (
            datetime.datetime.utcnow().timestamp() - data["last_change"]
            >= delay - delay * 0.1
        ):
            await actual_handler(e, i)

    return wrapper


def split_boosts(n):
    a = randint(0, n)
    b = randint(0, n - a)
    c = n - a - b
    return [a, b, c]


def get_key(iterable, obj: dict):
    for z in iterable:
        try:
            for x, y in obj.items():
                if z[x] == y:
                    ...
            return z
        except KeyError:
            ...
    return None


def get_attr(iterable, **kwargs):
    for z in iterable:
        try:
            for x, y in kwargs.items():
                if getattr(z, x) != y:
                    raise ValueError
            return z
        except ValueError:
            ...
    return None
