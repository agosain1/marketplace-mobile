"""
MailerSend Email Service
Handles email sending using MailerSend API
"""
import os
from mailersend import MailerSendClient, EmailBuilder
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

class MailerSendService:
    def __init__(self):
        self.api_key = os.getenv("MAILERSEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL")
        self.from_name = os.getenv("FROM_NAME", "Unimarket")

        if not self.api_key:
            raise ValueError("MAILERSEND_API_KEY environment variable is required")
        if not self.from_email:
            raise ValueError("FROM_EMAIL environment variable is required")

    def send_verification_email(self, recipient_email: str, verification_code: str, first_name: str) -> bool:
        """
        Send verification email using MailerSend API
        
        Args:
            recipient_email: Email address to send to
            verification_code: 6-digit verification code
            first_name: Recipient's first name
            
        Returns:
            bool: True if sent successfully, False otherwise
            
        Raises:
            HTTPException: If email sending fails
        """
        try:
            # Create MailerSend client
            ms = MailerSendClient(api_key=self.api_key)
            
            # Configure sender
            mail_from = {
                "name": self.from_name,
                "email": self.from_email,
            }
            
            # Configure recipient
            recipient = {
                    "name": first_name,
                    "email": recipient_email,
            }
            
            # Email content
            subject = "Verify Your Unimarket Account"
            html_content = self._get_verification_html(first_name, verification_code)
            plain_content = self._get_verification_plain_text(first_name, verification_code)


            email = (EmailBuilder()
                     .from_email(mail_from["email"], mail_from["name"])
                     .to_many([{"email": recipient["email"], "name": recipient["name"]}])
                     .subject(subject)
                     .html(html_content)
                     .text(plain_content)
                     .build())
            
            # Send the email
            response = ms.emails.send(email)
            
            # Check if send was successful
            if response and hasattr(response, 'status_code'):
                if response.status_code in [200, 201, 202]:
                    return True
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to send email. Status: {response.status_code}"
                    )
            
            # If no clear response, assume success (MailerSend API behavior)
            return True
            
        except Exception as e:
            print(f"MailerSend error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email sending failed: {str(e)}"
            )

    def _get_verification_html(self, first_name: str, verification_code: str) -> str:
        """Generate HTML content for verification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Account</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    color: #333;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #4CAF50;
                    text-align: center;
                    letter-spacing: 4px;
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    border: 2px dashed #4CAF50;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Unimarket!</h1>
                </div>
                <h2>Hi {first_name},</h2>
                <p>Thank you for signing up for Unimarket. To complete your registration, please verify your email address using the code below:</p>
                
                <div class="code">
                    {verification_code}
                </div>
                
                <p>This verification code will expire in 10 minutes.</p>
                <p>If you didn't create an account with Unimarket, please ignore this email.</p>
                
                <div class="footer">
                    <p>Best regards,<br>The Unimarket Team</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _get_verification_plain_text(self, first_name: str, verification_code: str) -> str:
        """Generate plain text content for verification email"""
        return f"""
Welcome to Unimarket!

Hi {first_name},

Thank you for signing up for Unimarket. To complete your registration, please verify your email address using the code below:

Verification Code: {verification_code}

This verification code will expire in 10 minutes.

If you didn't create an account with Unimarket, please ignore this email.

Best regards,
The Unimarket Team
        """.strip()


# Global instance
_email_service = None


def get_email_service() -> MailerSendService:
    """Get singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = MailerSendService()
    return _email_service