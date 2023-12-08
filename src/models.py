from typing import Optional

from pydantic import BaseModel, Field


class Model(BaseModel):
    id: Optional[str] = Field(default=None, alias="product_id")

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
    image_id: str
    date: str


class User(Model):
    user_id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]


class Admin(Model):
    user_id: int
