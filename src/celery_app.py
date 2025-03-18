from celery import Celery

import logging

from weather import get_weather_data

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@app.task
def add(x, y):
  try:
    if y==0:
      raise ValueError('A very specific bad thing happened.')
    else:
        return x + y
  except Exception as e:
    logging.exception('y is 0')
    return None


@app.task
def request_api_weather(latitude, longitude):
  try:
    weather_data = get_weather_data(latitude, longitude)
    return weather_data
  except Exception as e:
    logging.exception(f"Failure to fetch data from the Open-Meteo API - {e}")
    return None
