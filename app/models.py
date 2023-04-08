from pydantic import BaseModel
from datetime import datetime


class Registration(BaseModel):
    email: str
    password: str
    name: str
    surname: str
    mobile: str

class Login(BaseModel):
    email: str
    password: str

class PriceFeeds(BaseModel):
    timestamp: datetime
    target: str
    rates: dict