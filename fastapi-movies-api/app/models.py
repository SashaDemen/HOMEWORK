from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional

CURRENT_YEAR = datetime.utcnow().year

class MovieBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    director: str = Field(min_length=1, max_length=120)
    release_year: int = Field(ge=1888, le=CURRENT_YEAR)  # перший фільм ~1888
    rating: float = Field(ge=0, le=10)

    @field_validator("title", "director")
    @classmethod
    def non_blank(cls, v: str) -> str:
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

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

class MovieOut(Movie):
    pass
