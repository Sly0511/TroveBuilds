from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional
from .user import User
import re
import requests
import base64
from random import sample
from string import ascii_lowercase, ascii_uppercase, digits


get_category = re.compile(r".*?\/(.*?)\/.*")


blacklist = [
    "banner",
    "companion",
    "currency",
    "egg",
    "events",
    "equipment",
    "vendor",
    "npc",
    "hub",
    "bottleworld",
    "blueprint",
    "gem",
    "fixture",
    "quest",
    "reliquary",
    "rewardcrate",
    "Geode Mining Block",
    "hastener",
    "holiday",
    "influencer",
    "key",
    "matchmaker_delve_dial_depth_interactable",
    "Mining Block",
    "terraforming",
    "tutorial",
    "test",
]


class Item(Document):
    identifier: Indexed(str, unique=True)
    name: str
    type: str
    description: str
    icon: str
    notrade: str
    noobtain: str
    reported: bool = False
    hidden: bool = False
    verified: bool = False

    @property
    def trovesaurus_url(self):
        return "/".join(["https://trovesaurus.com/collections"] + self.identifier.split("/")[1:])

    @property
    def icon_url(self):
        return "https://trovesaurus.com/data/catalog/" + self.icon

    @property
    def icon_base64(self):
        response = requests.get(self.icon_url, stream=True)
        return base64.b64encode(response.content).decode("utf-8")

    @property
    def category(self):
        return self.type

    @property
    def blacklisted(self):
        return self.category in blacklist

    @property
    def tradeable(self):
        return not bool(int(self.notrade))

    @property
    def obtainable(self):
        return not bool(int(self.noobtain))

    @property
    def marketable(self):
        return self.tradeable and self.obtainable and not self.hidden and not self.blacklisted


class ListingStatus(Enum):
    listed = "Listed"
    pending = "Pending"
    sold = "Sold"
    cancelled = "Cancelled"
    expired = "Expired"


def generate_id():
    chars = ascii_uppercase + ascii_lowercase + digits
    return "".join(sample(chars, 7))


class PurchaseStatus(Enum):
    done = "Done"
    pending = "Pending"
    cancelled = "Cancelled"


class Purchase(BaseModel):
    buyer: Link[User]
    amount: int
    status: PurchaseStatus = PurchaseStatus.pending
    purchased_at: datetime = Field(default_factory=datetime.utcnow)


class Listing(Document):
    uuid: str = Field(default_factory=generate_id)
    item: Link[Item]
    seller: Link[User]
    buyers: list[Purchase] = []
    price: int
    amount: int
    status: ListingStatus = ListingStatus.listed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rating: Optional[int] = None
    finished: Optional[datetime] = None

    @property
    def price_per(self):
        return round(self.price / self.amount, 2)

    @property
    def better_price(self):
        return divmod(self.price, 9999)

    @property
    def tank_price(self):
        return self.better_price[0]

    @property
    def leftover_price(self):
        return self.better_price[1]
