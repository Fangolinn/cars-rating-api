from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..dependencies import get_db

router = APIRouter(tags=["cars"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_car(car: schemas.CarCreate, db: Session = Depends(get_db)) -> schemas.Car:
    db_car = models.Car(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@router.post("/{car_id}/rate", status_code=status.HTTP_201_CREATED)
def create_rating(
    car_id: int, rating: schemas.CarRatingCreate, db: Session = Depends(get_db)
) -> schemas.CarRating:
    if db.get(models.Car, car_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with id {car_id} not found.",
        )

    db_rating = models.CarRating(**rating.model_dump(), car_id=car_id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@router.get("/top10", status_code=status.HTTP_200_OK)
def get_top10_rated_cars(
    db: Session = Depends(get_db),
) -> list[schemas.CarWithAverageRating]:
    average_car_rating = func.avg(models.CarRating.rating)

    top_cars = (
        db.query(
            models.Car.id,
            models.Car.brand,
            models.Car.model,
            models.Car.production_year,
            average_car_rating.label("average_rating"),
        )
        .join(models.CarRating)
        .group_by(models.Car.id)
        .order_by(average_car_rating.desc())
        .order_by(models.Car.id)
        .limit(10)
        .all()
    )

    return top_cars
