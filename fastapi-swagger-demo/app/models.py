from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

CURRENT_YEAR = datetime.utcnow().year

# базова модель без id (для створення)
class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Назва фільму")
    director: str = Field(..., min_length=1, max_length=120, description="Режисер")
    release_year: int = Field(..., ge=1888, le=CURRENT_YEAR, description="Рік виходу (не майбутній)")
    rating: float = Field(..., ge=0, le=10, description="Оцінка 0..10")

    @field_validator("title", "director")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v

    @field_validator("release_year")
    @classmethod
    def not_future(cls, v: int) -> int:
        if v > datetime.utcnow().year:
            raise ValueError("release_year cannot be in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Interstellar",
                "director": "Christopher Nolan",
                "release_year": 2014,
                "rating": 8.6
            }
        }

# повна модель з id (для відповідей)
class Movie(MovieCreate):
    id: int = Field(..., description="Унікальний ID")
