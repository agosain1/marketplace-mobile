from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .database import get_db_cursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.post("/listings")
def create_listing(listing: Listing):
    new_listing = (listing.title, listing.description, listing.price, 'USD', listing.category, listing.location,
                   'new', 'active', 0, 'b3cfa2be-8a5f-4e3a-9020-8f84c234c678', ["https://placebear.com/g/200/200"])
    with get_db_cursor() as cur:
        cur.execute(INSERT_COMMAND, new_listing)
    return {"message": "Listing added successfully", "listing": new_listing}

@app.get("/listings")
def get_listings():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM listings")
        response = cur.fetchall()
    return response