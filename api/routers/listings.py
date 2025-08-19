from pydantic import BaseModel
from fastapi import APIRouter, Depends
from api.database import get_db_cursor
from .auth import verify_jwt_token
from fastapi import HTTPException, status

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

@router.get("/my_listings")
def get_my_listings(token_data: dict = Depends(verify_jwt_token)):
    user_id = token_data['uuid']
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM listings WHERE seller_id = %s", (user_id, ))
        response = cur.fetchall()
    return response

@router.delete("/{listing_id}")
def delete_listing(listing_id: str, token_data: dict = Depends(verify_jwt_token)):
    user_id = token_data['uuid']
    
    with get_db_cursor() as cur:
        # First check if the listing exists and belongs to the user
        cur.execute("SELECT seller_id FROM listings WHERE id = %s", (listing_id,))
        listing = cur.fetchone()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Check if the user owns this listing
        if listing['seller_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own listings"
            )
        
        # Delete the listing
        cur.execute("DELETE FROM listings WHERE id = %s", (listing_id,))
        
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
    
    return {"message": "Listing deleted successfully"}