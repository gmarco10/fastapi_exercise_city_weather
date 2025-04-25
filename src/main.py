from src.urls import router
from fastapi import FastAPI


# FastAPI instance
app = FastAPI()

app.include_router(router)

#todo: missing user and post crud actions
