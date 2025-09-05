from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
        "user": user
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

@router.put('/upload_pfp')
async def upload_pfp(
    image: UploadFile = File(...),
    token_data: dict = Depends(verify_jwt_token),
    db: Session = Depends(get_db)
):
    """Upload and update user profile picture"""
    user_id = token_data['uuid']

    # Find the user
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        from api.services.s3_service import get_s3_service
        s3_service = get_s3_service()
        
        # Delete old profile picture if it exists
        if user.pfp_url and isinstance(user.pfp_url, list) and len(user.pfp_url) > 0:
            old_image_url = user.pfp_url[0]
            try:
                s3_service.delete_image(old_image_url)
                print(f"Deleted old profile picture: {old_image_url}")
            except Exception as e:
                print(f"Warning: Failed to delete old profile picture: {str(e)}")
        
        # Upload new profile picture
        file_content = await image.read()
        file_extension = image.filename.split('.')[-1].lower()
        image_url = s3_service.upload_profile_picture(file_content, file_extension, user_id)
        
        # Update user's profile picture URL in database
        user.pfp_url = [image_url]  # Store as array to match the model
        db.commit()
        
        return {
            "message": "Profile picture updated successfully",
            "pfp_url": image_url
        }
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 service not available"
        )
    except Exception as e:
        print(f"Error uploading profile picture: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )