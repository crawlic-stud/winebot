from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="object_id")

    @classmethod
    def get_collection(cls):
        return cls.__name__.lower() + "s"


class Product(Model):
    name: str
    description: str
    image_id: str
    price: int


class Event(Model):
    name: str
    description: str
    image_id: str
    date: datetime


class User(Model):
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    last_active: datetime


class Admin(Model):
    user_id: int


class UserStat(Model):
    d: str
    users: list[str] = Field(default_factory=list)
