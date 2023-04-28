from beanie import Document, Link
from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from .user import User
import re


get_category = re.compile(r".*?\/(.*?)\/.*")


blacklist = [
    None,
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


class Item(BaseModel):
    identifier: str
    name: str
    description: str
    icon: str

    @property
    def icon_url(self):
        return "https://trovesaurus.com/data/catalog/" + self.icon

    @property
    def category(self):
        r = get_category.match(self.identifier)
        return r.group(1) if r else None

    @property
    def is_valid(self):
        if self.category in blacklist:
            return False
        return not "notrade" in self.identifier.lower()


class ListingStatus(Enum):
    listed = "Listed"
    pending = "Pending"
    sold = "Sold"
    expired = "Expired"
    cancelled = "Cancelled"


class Listing(Document):
    uuid: UUID = Field(default_factory=uuid4)
    item: str
    seller: Link[User]
    buyer: Optional[Link[User]] = None
    price: int
    amount: int
    status: ListingStatus = ListingStatus.listed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rating: Optional[int] = None
    finished: Optional[datetime] = None

    @property
    def price_per(self):
        return round(self.price / self.amount, 2)
