import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app, db_session, City, Base

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[db_session] = lambda: next(override_db_session())

client = TestClient(app)

@pytest.fixture
def sample_city(test_db):
  db = next(override_db_session())
  city = City(name="Test City", country="TC", latitude=12.34, longitude=56.78)
  db.add(city)
  db.commit()
  db.refresh(city)
  return city


def test_create_city_model(test_db):
  db = next(override_db_session())
  city = City(name="New City", country="NC", latitude=10.0, longitude=20.0)
  db.add(city)
  db.commit()
  db.refresh(city)

  assert city.id is not None
  assert city.name == "New City"
  assert city.country == "NC"

def test_create_city(test_db):
  response = client.post("/cities/", json={
      "name": "Sample City",
      "latitude": 10.0,
      "longitude": 20.0,
      "country": "SC"
  })
  assert response.status_code == 201
  data = response.json()
  assert data["name"] == "Sample City"
  assert data["country"] == "SC"

def test_get_city(sample_city):
  response = client.get(f"/cities/{sample_city.id}")
  assert response.status_code == 200
  data = response.json()
  assert data["id"] == sample_city.id
  assert data["name"] == "Test City"


def test_get_cities(sample_city):
    response = client.get("/cities/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_city(sample_city):
    response = client.put(f"/cities/{sample_city.id}", json={
        "name": "Updated City",
        "latitude": 15.0,
        "longitude": 25.0,
        "country": "UC"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated City"


def test_delete_city(sample_city):
    response = client.delete(f"/cities/{sample_city.id}")
    assert response.status_code == 204

# mockear desde donde se usa (el metodo get_weather_data en main), y no desde donde se crea (no mokear en weather.py)


def test_city_weather_success(sample_city):
  """Test city_weather endpoint with a mocked weather API response."""
  mock_weather_data = {
      "temperature": 22.5,
      "humidity_percentage": 60,
      "weather_condition": "clear",
      "wind_speed": 5.0
  }

  # Mock get_weather_data
  with patch("src.main.get_weather_data", return_value=mock_weather_data):
      response = client.get(f"/cities/{sample_city.id}/weather")

  assert response.status_code == 200
#   assert response.json().keys() == mock_weather_data
