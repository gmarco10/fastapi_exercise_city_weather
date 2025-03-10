
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class CityBaseSchema(BaseModel):
    id: int
    name: str

class CityParamsSchema(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None

class CityExtendedSchema(CityParamsSchema):
    id: int
    created_at: datetime
    updated_at: datetime

class WeatherResponseSchema(BaseModel):
    temperature: float
    weather_condition: float
    wind_speed: float
    humidity_percentage: float

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    owner_id: int

class PostResponse(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    posts: list[PostResponse] = []
    visited_cities: list[CityBaseSchema]

    class Config:
        orm_mode = True
