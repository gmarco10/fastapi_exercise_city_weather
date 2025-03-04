import requests
from retry_requests import retry

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
      response = requests.get(url, params=params)
      response.raise_for_status()
      data = response.json()
    except requests.exceptions.RequestException as e:
      print(f"request error: {e}")

    if "current" not in data:
      raise KeyError("Missing 'current' key in API response")

    current = data.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "humidity_percentage": current.get("relative_humidity_2m"),
        "weather_condition": current.get("weather_code"),
        "wind_speed": current.get("wind_speed_10m")
    }
