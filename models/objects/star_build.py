from beanie import Document, Indexed
from pydantic import Field
from utils.functions import random_id


class StarBuild(Document):
    build: Indexed(str, unique=True) = Field(default_factory=random_id)
    paths: list[str]
