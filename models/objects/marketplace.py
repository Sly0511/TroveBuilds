from beanie import Document
from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime


class ListingStatus(Enum):
    listed = "Listed"
    sold = "Sold"
    expired = "Expired"
    cancelled = "Cancelled"


class Listing(Document):
    uuid: UUID = Field(default_factory=uuid4)
    price: int
    price_per: float
    amount: int
    status: ListingStatus = ListingStatus.listed
    datetime: datetime = Field(default_factory=datetime.utcnow)
