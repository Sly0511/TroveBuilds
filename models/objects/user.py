from beanie import Document, Indexed
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MarketplaceData(BaseModel):
    listings: list[UUID] = []


class User(Document):
    uuid: Indexed(UUID, unique=True) = Field(default_factory=uuid4)
    discord_id: Optional[Indexed(int, unique=True)] = None
    trovesaurus_id: Optional[Indexed(str, unique=True)] = None
    market: MarketplaceData = Field(default_factory=MarketplaceData)
    blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
