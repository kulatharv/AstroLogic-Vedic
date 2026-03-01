from pydantic import BaseModel
from typing import Optional


class BirthData(BaseModel):
    name: Optional[str] = "Seeker"
    year: int
    month: int
    day: int
    hour: float
    place: Optional[str] = "Unknown"