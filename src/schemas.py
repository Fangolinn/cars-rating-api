from pydantic import BaseModel, ConfigDict, Field, field_validator


class CarCreate(BaseModel):
    brand: str = Field(max_length=50)
    model: str = Field(max_length=100)
    production_year: int = Field(ge=1500)


class Car(CarCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CarRatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)


class CarRating(CarRatingCreate):
    id: int
    car_id: int


class CarWithAverageRating(Car):
    average_rating: float

    @field_validator("average_rating")
    def round_average_rating(cls, value) -> float:
        return round(value, 2)
