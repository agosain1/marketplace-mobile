from pydantic import BaseModel
from typing import Optional

class Listing(BaseModel):
    title: str
    description: str
    price: float
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition: str