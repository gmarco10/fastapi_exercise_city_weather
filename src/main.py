# database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/city_weather_db"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# city table
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, func, asc, desc, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


from weather import get_weather_data

Base = declarative_base()

user_cities = Table(
    "user_cities",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("city_id", Integer, ForeignKey("cities.id"), primary_key=True)
)

class City(Base):
  __tablename__ = "cities"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  country = Column(String, nullable=True)
  latitude = Column(Float, nullable=False)
  longitude = Column(Float, nullable=False)

  user_visitors = relationship("User", secondary=user_cities, back_populates="visited_cities")

  created_at = Column(DateTime, server_default=func.now(), nullable=False)
  updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)


class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)

  posts = relationship("Post", back_populates="owner")
  visited_cities = relationship("City", secondary=user_cities, back_populates="user_visitors")

  created_at = Column(DateTime, server_default=func.now(), nullable=False)
  updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)


class Post(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, index=True)
  content = Column(String)

  owner_id = Column(Integer, ForeignKey("users.id"))
  owner = relationship("User", back_populates="posts")

  created_at = Column(DateTime, server_default=func.now(), nullable=False)
  updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)


# city model (pydantic)
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

class CityIdSchema(BaseModel):
   id: int

class CityExtendedSchema(CityParamsSchema, CityIdSchema):
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

class WeatherResponseSchema(BaseModel):
    temperature: float
    weather_condition: float
    wind_speed: float
    humidity_percentage: float

from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, HTTPException, status


# FastAPI instance
app = FastAPI()


# API Endpoints
@app.get("/cities/{id}", response_model = CityExtendedSchema)
def get_city(id: int) -> CityExtendedSchema:
    cities_query = session.query(City)
    city = cities_query.filter(City.id == id).first()
    if not city:
      raise HTTPException(status_code=404, detail="City not found")
    return city.__dict__

@app.get("/cities/", response_model=list[CityBaseSchema])
def get_cities(
    name: Optional[str] = None,
    country: Optional[str] = None,
    sort_by: str = "id",
    order: str = "asc"
):
    cities_query = session.query(City)

    if name:
        cities_query = cities_query.filter(City.name.ilike(f"%{name}%"))
    if country:
        cities_query = cities_query.filter(City.country.ilike(f"%{country}%"))

    if order == "desc":
        cities_query = cities_query.order_by(desc(getattr(City, sort_by, City.id)))
    else:
        cities_query = cities_query.order_by(asc(getattr(City, sort_by, City.id)))

    return cities_query.all()


@app.post("/cities/", response_model=CityExtendedSchema, status_code=status.HTTP_201_CREATED)
def create_city(city: CityParamsSchema):
  new_city = City(name=city.name, country=city.country, latitude=city.latitude, longitude=city.longitude)
  session.add(new_city)
  session.commit()
  session.refresh(new_city)
  return new_city.__dict__

@app.put("/cities/{id}", response_model=CityExtendedSchema)
def update_city(id: int, city: CityParamsSchema):
  cities_query = session.query(City)
  db_city = cities_query.filter(City.id == id).first()
  if not db_city:
      raise HTTPException(status_code=404, detail="City not found")

  db_city.name = city.name
  db_city.country = city.country
  db_city.latitude = city.latitude
  db_city.longitude = city.longitude

  session.commit()
  session.refresh(db_city)
  return db_city.__dict__

@app.delete("/cities/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(id: int):
  cities_query = session.query(City)
  db_city = cities_query.filter(City.id == id).first()
  if not db_city:
      raise HTTPException(status_code=404, detail="City not found")

  session.delete(db_city)
  session.commit()

@app.get("/cities/{id}/weather", response_model=WeatherResponseSchema )
def city_weather(id: int):
    cities_query = session.query(City)
    city = cities_query.filter(City.id == id).first()
    if not city:
      raise HTTPException(status_code=404, detail="City not found")

    try:
      weather_data = get_weather_data(city.latitude, city.longitude)
      return WeatherResponseSchema(
          temperature=weather_data["temperature"],
          humidity_percentage=weather_data["humidity_percentage"],
          weather_condition=weather_data["weather_condition"],
          wind_speed=weather_data["wind_speed"]
      )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failure to fetch data from the Open-Meteo API - {e}")

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


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):

  new_user = User(name=user.name)
  session.add(new_user)
  session.commit()
  session.refresh(new_user)
  return new_user.__dict__


@app.get("/users/", response_model=list[UserResponse])
def get_users():
    users_query = session.query(User)

    return users_query.all()

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    users_query = session.query(User)
    user = users_query.filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#todo: missing user and post crud actions
