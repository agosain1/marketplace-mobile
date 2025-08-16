from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Listing(BaseModel):
    title: str
    description: str
    price: float

listings = []

@app.post("/listings")
def create_listing(listing: Listing):
    new_listing = listing.dict()
    new_listing["id"] = len(listings) + 1
    listings.append(new_listing)
    return {"message": "Listing added successfully", "listing": new_listing}

@app.get("/listings")
def get_listings():
    return listings
