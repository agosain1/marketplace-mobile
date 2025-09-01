from pydantic import BaseModel
from fastapi import APIRouter, Depends, UploadFile, File, Form
from api.database import get_db_cursor
from .auth import verify_jwt_token_and_email
from fastapi import HTTPException, status
from api.services.s3_service import get_s3_service
from api.services.location_service import get_location_from_coords, search_location, search_location_suggestions
from typing import List, Optional
import uuid

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

INSERT_COMMAND = """
        INSERT INTO listings (title, description, price, currency, category, latitude, longitude, condition, status, views, seller_id, images, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

class Listing(BaseModel):
    title: str
    description: str
    price: float
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition: str
    seller_id: str

@router.post("")
async def create_listing(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    condition: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    token_data: dict = Depends(verify_jwt_token_and_email)
):
    seller_id = token_data['uuid']
    listing_id = str(uuid.uuid4())
    image_urls = []
    
    try:
        # Handle image uploads if provided
        if images and len(images) > 0 and images[0].filename:
            # Validate image files
            allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
            max_file_size = 5 * 1024 * 1024  # 5MB
            
            image_urls = []
            
            for image in images:
                # Check file size
                if hasattr(image, 'size') and image.size > max_file_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Image {image.filename} is too large. Maximum size is 5MB."
                    )
                
                # Check file extension
                file_extension = image.filename.split('.')[-1].lower()
                if file_extension not in allowed_extensions:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
                    )
                
                # Read file content
                file_content = await image.read()
                
                # Upload to S3
                image_url = get_s3_service().upload_listing_image(file_content, file_extension, listing_id)
                image_urls.append(image_url)
        

        location = get_location_from_coords(latitude, longitude)
        # Insert listing into database
        new_listing = (
            title, description, price, 'USD', category, latitude, longitude,
            condition, 'active', 0, seller_id, image_urls, location
        )
        
        with get_db_cursor() as cur:
            cur.execute(INSERT_COMMAND, new_listing)
        
        response_data = {
            "message": "Listing created successfully",
            "listing_id": listing_id
        }
        
        # Add images to response if they were uploaded
        if images and len(images) > 0 and images[0].filename:
            response_data["images"] = image_urls
        
        return response_data
        
    except Exception as e:
        # Clean up any uploaded images if database insert fails
        if 'image_urls' in locals() and images and len(images) > 0:
            # Only clean up actual uploaded images, not placeholders
            uploaded_images = [url for url in image_urls]
            if uploaded_images:
                get_s3_service().delete_listing_images(uploaded_images)
        
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create listing: {str(e)}"
        )

@router.get("")
def get_listings():
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT 
                l.*,
                CONCAT(u.fname, ' ', u.lname) as seller_name,
                u.email as seller_email
            FROM listings l
            JOIN users u ON l.seller_id = u.id
            ORDER BY l.created_at DESC
            """
        )
        response = cur.fetchall()
    return response

@router.get("/my_listings")
def get_my_listings(token_data: dict = Depends(verify_jwt_token_and_email)):
    user_id = token_data['uuid']
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM listings WHERE seller_id = %s", (user_id, ))
        response = cur.fetchall()
    return response

@router.get("/{listing_id}")
def get_listing(listing_id: str):
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT 
                l.*,
                CONCAT(u.fname, ' ', u.lname) as seller_name,
                u.email as seller_email
            FROM listings l
            JOIN users u ON l.seller_id = u.id
            WHERE l.id = %s
            """,
            (listing_id,)
        )
        listing = cur.fetchone()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
    return listing

@router.delete("/{listing_id}")
def delete_listing(listing_id: str, token_data: dict = Depends(verify_jwt_token_and_email)):
    user_id = token_data['uuid']
    
    with get_db_cursor() as cur:
        # First check if the listing exists and belongs to the user
        cur.execute("SELECT seller_id, images FROM listings WHERE id = %s", (listing_id,))
        listing = cur.fetchone()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Check if the user owns this listing (convert both to strings for comparison)
        if str(listing['seller_id']) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own listings"
            )
        
        # Get image URLs before deleting
        image_urls = listing.get('images', [])
        
        # Delete the listing
        cur.execute("DELETE FROM listings WHERE id = %s", (listing_id,))
        
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Listing not found"
            )
        
        # Delete images from S3
        if image_urls and isinstance(image_urls, list):
            # Filter out placeholder images
            s3_images = [url for url in image_urls]
            if s3_images:
                get_s3_service().delete_listing_images(s3_images)
    
    return {"message": "Listing deleted successfully"}

@router.get("/search-location/{query}")
def search_location_endpoint(query: str):
    """
    Search for a location and return coordinates
    """
    result = search_location(query)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return result

@router.get("/location-suggestions/{query}")
def get_location_suggestions(query: str, limit: int = 5):
    """
    Get autocomplete suggestions for location search
    """
    suggestions = search_location_suggestions(query, limit)
    return {"suggestions": suggestions}