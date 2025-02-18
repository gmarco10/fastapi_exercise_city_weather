# fastapi_exercise_city_weather
fastapi exercise


```
$ pip install -r requirements.txt

$ alembic init alembic

```

Create database
```
$ sudo -u postgres psql -c "CREATE DATABASE city_weather_db;"

```


Edit alembic.ini to have the DATABASE URL

Generate migration:
and apply
```
$ alembic revision --autogenerate -m "create cities table"

$ alembic upgrade head


```
