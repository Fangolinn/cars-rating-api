from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "car"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    production_year: Mapped[int]

    ratings: Mapped[list[CarRating]] = relationship(
        "CarRating", back_populates="car", cascade="all, delete-orphan"
    )


class CarRating(Base):
    __tablename__ = "car_rating"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[Car] = mapped_column(Integer, ForeignKey("car.id"))
    rating: Mapped[int]

    car: Mapped[Car] = relationship("Car", back_populates="ratings")
