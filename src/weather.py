import requests
import requests_cache
from retry_requests import retry

cache_session = requests_cache.CachedSession("weather_cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

def get_weather_data(latitude: float, longitude: float):
  url = "https://api.open-meteo.com/v1/forecast"
  params = {
      "latitude": latitude,
      "longitude": longitude,
      "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
      "timezone": "auto",
      "past_days": 92
  }

  try:
    response = retry_session.get(url, params=params)
    response.raise_for_status()
    data = response.json()
  except requests.exceptions.RequestException as e:
    raise Exception(f"request error: {e}")

  if "current" not in data:
    raise KeyError("Missing 'current' key in API response")

  current = data.get("current", {})
  return {
      "temperature": current.get("temperature_2m"),
      "humidity_percentage": current.get("relative_humidity_2m"),
      "weather_condition": current.get("weather_code"),
      "wind_speed": current.get("wind_speed_10m")
  }
