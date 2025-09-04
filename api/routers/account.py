from fastapi import APIRouter, Depends, HTTPException, status
from api.models import Users, Listings, Messages
from .auth import verify_jwt_token
from sqlalchemy.orm import Session
from api.database import get_db
from pydantic import BaseModel


router = APIRouter(
    prefix = "/account",
    tags = ["account"]
)

class UpdateProfile(BaseModel):
    firstName: str
    lastName: str


@router.delete('/delete-account')
def delete_account(token_data: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    """Delete user account and all associated data"""
    user_id = token_data['uuid']

    # Import S3 service here to avoid circular imports
    s3_service = None
    try:
        from api.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        s3_available = True
    except ImportError:
        s3_available = False
        print("S3 service not available, skipping image cleanup")

    # Find the user
    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    # Get all listing images to delete from S3
    all_image_urls = []
    if s3_available:
        user_listings = db.query(Listings).filter(Listings.seller_id == user_id).all()

        for listing in user_listings:
            if listing.images and isinstance(listing.images, list):
                all_image_urls.extend(listing.images)

    # Delete all user's listings from database (cascade will handle this)
    db.query(Listings).filter(Listings.seller_id == user_id).delete()

    # Delete all messages where user is sender OR receiver
    db.query(Messages).filter(Messages.sender_id == user_id).delete()
    db.query(Messages).filter(Messages.receiver_id == user_id).delete()

    # Delete the user account
    db.delete(user)
    db.commit()

    # Delete images from S3 after database transaction is complete
    if s3_available and all_image_urls:
        try:
            for image_url in all_image_urls:
                s3_service.delete_image(image_url)
            print(f"Deleted {len(all_image_urls)} images from S3 for deleted account")
        except Exception as e:
            print(f"Warning: Failed to delete some S3 images for deleted account: {str(e)}")

    return {"message": "Account successfully deleted"}


@router.get('/profile')
def get_profile(token_data: dict = Depends(verify_jwt_token), db: Session = Depends(get_db)):
    """Get user profile information"""
    user_id = token_data['uuid']

    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    return {
        "firstName": user.fname,
        "lastName": user.lname,
        "email": user.email,
        "isGoogleUser": bool(user.google_id)
    }


@router.put('/profile')
def update_profile(profile_data: UpdateProfile, token_data: dict = Depends(verify_jwt_token),
                   db: Session = Depends(get_db)):
    """Update user profile information"""
    user_id = token_data['uuid']

    user = db.query(Users).filter(Users.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    # Update user information
    user.fname = profile_data.firstName.strip()
    user.lname = profile_data.lastName.strip()
    db.commit()

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": str(user.id),
            "email": user.email
        }
    }