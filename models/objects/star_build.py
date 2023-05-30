from beanie import Document, Indexed
from pydantic import Field
from random import sample
from string import ascii_letters, digits


def random_id():
    return "".join(sample(ascii_letters + digits, k=8))


class StarBuild(Document):
    build: Indexed(str, unique=True) = Field(default_factory=random_id)
    paths: list[str]
