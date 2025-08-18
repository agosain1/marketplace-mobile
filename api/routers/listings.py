from pydantic import BaseModel
from fastapi import APIRouter

from api.database import get_db_cursor

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

INSERT_COMMAND = """
        INSERT INTO listings (title, description, price, currency, category, location, condition, status, views, seller_id, images)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

class Listing(BaseModel):
    title: str
    description: str
    price: float
    category: str
    location: str
    seller_id: str

@router.post("")
def create_listing(listing: Listing):
    new_listing = (listing.title, listing.description, listing.price, 'USD', listing.category, listing.location,
                   'new', 'active', 0, listing.seller_id, ["https://placebear.com/g/200/200"])
    with get_db_cursor() as cur:
        cur.execute(INSERT_COMMAND, new_listing)
    return {"message": "Listing added successfully", "listing": new_listing}

@router.get("")
def get_listings():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM listings")
        response = cur.fetchall()
    return response