from beanie import Document, Indexed
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .builds import BuildConfig


class MarketplaceData(BaseModel):
    buyer_upvotes: list[UUID] = []
    buyer_downvotes: list[UUID] = []
    seller_upvotes: list[UUID] = []
    seller_downvotes: list[UUID] = []

    @property
    def buyer_rating_valid(self):
        up = len(self.buyer_upvotes)
        down = len(self.buyer_upvotes)
        return up + down >= 5

    @property
    def buyer_rating(self):
        up = len(self.buyer_upvotes)
        down = len(self.buyer_upvotes)
        if not self.buyer_rating_valid:
            raise ValueError("Not enough votes")
        return round(round(up / (up + down) * 5 * 2) / 2, 1)

    @property
    def seller_rating_valid(self):
        up = len(self.seller_upvotes)
        down = len(self.seller_downvotes)
        return up + down >= 5

    @property
    def seller_rating(self):
        up = len(self.seller_upvotes)
        down = len(self.seller_downvotes)
        if not self.seller_rating_valid:
            raise ValueError("Not enough votes")
        return round(round(up / (up + down) * 5 * 2) / 2, 1)


class SavedBuild(Document):
    uuid: Indexed(UUID, unique=True) = Field(default_factory=uuid4)
    build: BuildConfig
    public: bool = False
    created_at: datetime


class User(Document):
    uuid: Indexed(UUID, unique=True) = Field(default_factory=uuid4)
    discord_id: Indexed(int, unique=True, partialFilterExpression={"discord_id": {"$type": "long"}}) = None
    trovesaurus_id: Indexed(str, unique=True, partialFilterExpression={"trovesaurus_id": {"$type": "string"}}) = None
    market: MarketplaceData = Field(default_factory=MarketplaceData)
    blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
