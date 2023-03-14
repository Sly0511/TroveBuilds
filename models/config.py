from enum import Enum

from pydantic import BaseModel


class Locale(Enum):
    American_English = "en_US"
    German = "de_DE"
    Portuguese = "pt_PT"
    Russian = "ru_RU"
    French = "fr_FR"


class Config(BaseModel):
    locale: Locale = Locale.American_English