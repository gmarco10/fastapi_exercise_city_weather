# fastapi_exercise_city_weather
fastapi exercise


```
$ pip install -r requirements.txt

$ alembic init alembic

```

Create database
```
$ docker run --name fastapi-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=city_weather_db -p 5432:5432 -d postgres

```

Edit alembic.ini to have the DATABASE URL

Generate migration:
and apply
```
$ alembic revision --autogenerate -m "create cities table"

$ alembic upgrade head
```


To rollback migration:
```
$ alembic downgrade -N
```

run server:
from root:
```
$ uvicorn src.main:app --reload
```

run tests:
from root:
```
$ pytest
```
