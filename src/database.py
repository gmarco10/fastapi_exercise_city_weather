from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from typing import Iterator

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/city_weather_db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# per-request session
def db_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
