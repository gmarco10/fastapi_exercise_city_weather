# database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/city_weather_db"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# city table
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, func, asc, desc
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class City(Base):
  __tablename__ = "cities"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  country = Column(String, nullable=True)
  latitude = Column(Float, nullable=False)
  longitude = Column(Float, nullable=False)
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

#### celery api

from celery_app import add, request_api_weather
from celery.result import AsyncResult
from celery_app import add

@app.get("/cities/{id}/weather", response_model=dict )
def city_weather(id: int):
    cities_query = session.query(City)
    city = cities_query.filter(City.id == id).first()
    if not city:
      raise HTTPException(status_code=404, detail="City not found")

    task = request_api_weather.delay(city.latitude, city.longitude)
    return {"task_id": task.id, "message": "Queued task."}

@app.get("/cities/weather_celery_response/{task_id}", response_model=WeatherResponseSchema )
def city_weather_response(task_id: str):
    task_result = AsyncResult(task_id, app=request_api_weather)
    if task_result.ready():
        return WeatherResponseSchema(
            temperature=task_result.result["temperature"],
            humidity_percentage=task_result.result["humidity_percentage"],
            weather_condition=task_result.result["weather_condition"],
            wind_speed=task_result.result["wind_speed"]
            )

@app.post("/sum/")
def calculate_sum(x: int, y: int):
    task = add.delay(x, y)
    return {"task_id": task.id, "message": "Queued task."}

@app.get("/result/{task_id}")
def get_result(task_id: str):

    task_result = AsyncResult(task_id, app=add)
    if task_result.ready():
        return {"task_id": task_id, "result": task_result.result}
    return {"task_id": task_id, "status": "task_result.status"}
