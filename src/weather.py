import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_weather_data(latitude: float, longitude: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
      "latitude": latitude,
      "longitude": longitude,
      "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
      "timezone": "auto",
      "past_days": 92
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]  # Process first location response
    current = response.Current()

    return {
        "temperature": current.Variables(0).Value(),
        "humidity_percentage": current.Variables(1).Value(),
        "weather_condition": current.Variables(2).Value(),
        "wind_speed": current.Variables(3).Value()
    }
