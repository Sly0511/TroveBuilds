from beanie import Document
from uuid import UUID, uuid4
from pydantic import Field, SecretField
from datetime import datetime


class User(Document):
    uuid: UUID = Field(default_factory=uuid4)
    username: str
    password: SecretField(str)
    token: SecretField(str)
    created_at: datetime = Field(default_factory=datetime.utcnow)

