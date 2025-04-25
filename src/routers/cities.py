from fastapi import APIRouter, Depends, HTTPException, status
from src.database import db_session
from src.models import City
from src.schemas import CityExtendedSchema, CityParamsSchema, CityBaseSchema, WeatherResponseSchema
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from typing import Optional

from src.external.weather import get_weather_data

router = APIRouter()

@router.get("/{id}", response_model = CityExtendedSchema)
def get_city(id: int, session: Session = Depends(db_session)) -> CityExtendedSchema:
    cities_query = session.query(City)
    city = cities_query.filter(City.id == id).first()
    if not city:
      raise HTTPException(status_code=404, detail="City not found")
    return city.__dict__

@router.get("/", response_model=list[CityBaseSchema])
def get_cities(
    name: Optional[str] = None,
    country: Optional[str] = None,
    sort_by: str = "id",
    order: str = "asc",
    session: Session = Depends(db_session)
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


@router.post("/", response_model=CityExtendedSchema, status_code=status.HTTP_201_CREATED)
def create_city(city: CityParamsSchema, session: Session = Depends(db_session)):
  new_city = City(name=city.name, country=city.country, latitude=city.latitude, longitude=city.longitude)
  session.add(new_city)
  session.commit()
  session.refresh(new_city)
  return new_city.__dict__

@router.put("/{id}", response_model=CityExtendedSchema)
def update_city(id: int, city: CityParamsSchema, session: Session = Depends(db_session)):
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

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(id: int, session: Session = Depends(db_session)):
  cities_query = session.query(City)
  db_city = cities_query.filter(City.id == id).first()
  if not db_city:
      raise HTTPException(status_code=404, detail="City not found")

  session.delete(db_city)
  session.commit()

@router.get("/{id}/weather", response_model=WeatherResponseSchema )
def city_weather(id: int, session: Session = Depends(db_session)):
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
