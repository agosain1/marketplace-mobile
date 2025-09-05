from pydantic import BaseModel
from fastapi import APIRouter, Depends, UploadFile, File, Form
from api.database import get_db
from api.models import Users, Listings
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .auth import verify_jwt_token
from fastapi import HTTPException, status
from api.services.s3_service import get_s3_service
from api.services.location_service import get_location_from_coords, search_location, search_location_suggestions, get_bounding_box_corners
from typing import List, Optional
import uuid

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)


class Listing(BaseModel):
    title: str
    description: str
    price: float
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    condition: str

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
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    seller_id = token_data['uuid']
    s3_id = str(uuid.uuid4())
    image_urls = []
    
    try:
        # Handle image uploads
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
                image_url = get_s3_service().upload_listing_image(file_content, file_extension, s3_id)
                image_urls.append(image_url)
        

        location = get_location_from_coords(latitude, longitude)
        
        # Create listing using SQLAlchemy
        new_listing = Listings(
            title=title,
            description=description,
            price=price,
            currency='USD',
            category=category,
            latitude=latitude,
            longitude=longitude,
            condition=condition,
            status='active',
            views=0,
            seller_id=uuid.UUID(seller_id),
            images=image_urls,
            location=location
        )
        
        db.add(new_listing)
        db.commit()
        db.refresh(new_listing)
        
        response_data = {
            "message": "Listing created successfully",
            "listing_id": str(new_listing.id)
        }
        
        # Add images to response if they were uploaded
        if images and len(images) > 0 and images[0].filename:
            response_data["images"] = image_urls
        
        return response_data
        
    except Exception as e:
        # Clean up any uploaded images if database insert fails
        if 'image_urls' in locals() and images and len(images) > 0:
            if image_urls:
                for image in image_urls:
                    get_s3_service().delete_image(image)
        
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create listing: {str(e)}"
        )

@router.get("")
def get_listings(user_id: Optional[str] = None,
                 db: Session = Depends(get_db),
                 lat: Optional[float] = None,
                 lon: Optional[float] = None,
                 dist: Optional[float] = None
                 ):
    # Query listings with seller information using SQLAlchemy relationships
    query = (
        db.query(Listings)
        .join(Users, Listings.seller_id == Users.id)
        .order_by(Listings.created_at.desc())
    )

    if user_id:
        query = query.filter(Listings.seller_id != user_id)

    bounding_box = get_bounding_box_corners(lat, lon, dist)

    if bounding_box:
        ne, nw, se, sw = bounding_box['northeast'], bounding_box['northwest'], bounding_box['southeast'], bounding_box['southwest']
        lat_min = min(sw[0], se[0])
        lat_max = max(nw[0], ne[0])
        lng_min = min(nw[1], sw[1])
        lng_max = max(ne[1], se[1])

        query = query.filter(
            Listings.latitude.between(lat_min, lat_max),
            Listings.longitude.between(lng_min, lng_max)
        )

    listings = query.all()

    # Format response with seller information
    result = []
    for listing in listings:
        seller = db.query(Users).filter(Users.id == listing.seller_id).first()
        result.append(format_listing(listing, seller))

    return result


@router.get("/search")
def search_listing(q: str, user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = (
        db.query(Listings)
        .join(Users, Listings.seller_id == Users.id)
        .order_by(Listings.created_at.desc())
    )

    if user_id:
        query = query.filter(Listings.seller_id != user_id)

    if q:
        query = query.filter(
            or_(
                Listings.title.ilike(f"%{q}%"),
                Listings.description.ilike(f"%{q}%")
            )
        )

    listings = query.all()

    result = []
    for listing in listings:
        seller = db.query(Users).filter(Users.id == listing.seller_id).first()
        result.append(format_listing(listing, seller))

    return result

@router.get("/my_listings")
def get_my_listings(token_data: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    user_id = uuid.UUID(token_data['uuid'])
    
    # Query user's listings
    listings = db.query(Listings).filter(Listings.seller_id == user_id).all()

    # Get seller information (self)
    seller = db.query(Users).filter(Users.id == user_id).first()
    
    # Convert to dict format for response
    result = []
    for listing in listings:
        result.append(format_listing(listing, seller))

    return result

@router.get("/{listing_id}")
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    # Find the listing
    listing = db.query(Listings).filter(Listings.id == uuid.UUID(listing_id)).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Get seller information
    seller = db.query(Users).filter(Users.id == listing.seller_id).first()
    
    # Format response
    result = format_listing(listing, seller)
    
    return result

@router.delete("/{listing_id}")
def delete_listing(listing_id: str, token_data: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    user_id = uuid.UUID(token_data['uuid'])
    
    # Find the listing
    listing = db.query(Listings).filter(Listings.id == uuid.UUID(listing_id)).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )
    
    # Check if the user owns this listing
    if listing.seller_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own listings"
        )
    
    # Get image URLs before deleting
    image_urls = listing.images or []
    
    # Delete the listing
    db.delete(listing)
    db.commit()
    
    # Delete images from S3
    if image_urls and isinstance(image_urls, list):
        for url in image_urls:
            get_s3_service().delete_image(url)
    
    return {"message": "Listing deleted successfully"}

@router.get("/search-location/{query}")
def search_location_endpoint(query: str, db: Session = Depends(get_db)):
    """
    Search for a location and return coordinates
    """
    result = search_location(query, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return result

@router.get("/location-suggestions/{query}")
def get_location_suggestions(query: str, limit: int = 5, db: Session = Depends(get_db)):
    """
    Get autocomplete suggestions for location search
    """
    suggestions = search_location_suggestions(query, limit, db)
    return {"suggestions": suggestions}

def format_listing(listing: Listing, seller: str):
    return {
        "id": str(listing.id),
        "title": listing.title,
        "description": listing.description,
        "price": float(listing.price),
        "currency": listing.currency,
        "category": listing.category,
        "latitude": float(listing.latitude) if listing.latitude else None,
        "longitude": float(listing.longitude) if listing.longitude else None,
        "condition": listing.condition,
        "status": listing.status,
        "views": listing.views,
        "seller_id": str(listing.seller_id),
        "images": listing.images,
        "location": listing.location,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
        "seller_name": f"{seller.fname} {seller.lname}" if seller else None,
        "seller_email": seller.email if seller else None
    }