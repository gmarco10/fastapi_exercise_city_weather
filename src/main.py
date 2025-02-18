# database setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/city_weather_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
  db = SessionLocal()
  try:
    yield db
  finally:
      db.close()

# city table
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class City(Base):
  __tablename__ = "cities"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  country = Column(String, nullable=False)
  latitude = Column(Float, nullable=False)
  longitude = Column(Float, nullable=False)
  created_at = Column(DateTime, server_default=func.now())
  updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())
