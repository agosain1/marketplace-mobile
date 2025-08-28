import os
import boto3
from botocore.exceptions import ClientError
from typing import List
import uuid
from datetime import datetime

class S3Service:
    def __init__(self):
        # Check for required environment variables
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-west-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not aws_access_key:
            raise ValueError("AWS_ACCESS_KEY_ID environment variable is required")
        if not aws_secret_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY environment variable is required")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable is required")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
    def upload_listing_image(self, file_content: bytes, file_extension: str, listing_id: str) -> str:
        """
        Upload a listing image to S3 and return the public URL
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"listings/{listing_id}/{timestamp}_{unique_id}.{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=f'image/{file_extension}',
                ACL='public-read'
            )
            
            # Return public URL
            return f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{filename}"
            
        except ClientError as e:
            raise Exception(f"Failed to upload image: {str(e)}")
    
    def upload_multiple_images(self, files_data: List[tuple], listing_id: str) -> List[str]:
        """
        Upload multiple images and return list of URLs
        files_data: List of tuples (file_content: bytes, file_extension: str)
        """
        urls = []
        for file_content, file_extension in files_data:
            url = self.upload_listing_image(file_content, file_extension, listing_id)
            urls.append(url)
        return urls
    
    def delete_listing_images(self, image_urls: List[str]) -> bool:
        """
        Delete images from S3 given their URLs
        """
        try:
            for url in image_urls:
                # Extract key from URL
                key = url.split(f'{self.bucket_name}.s3')[1].split('.amazonaws.com/')[1]
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting images: {str(e)}")
            return False

# Create global instance with lazy initialization
s3_service = None

def get_s3_service():
    global s3_service
    if s3_service is None:
        s3_service = S3Service()
    return s3_service