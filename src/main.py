from fastapi import FastAPI

from .api import cars

app = FastAPI()


app.include_router(cars.router, prefix="/cars")
