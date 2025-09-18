from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, listings, messages, account
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Marketplace API",
    description="A marketplace application API",
    version="1.0.0"
)

origin = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Railway
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Marketplace API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Marketplace API", "docs": "/docs"}

app.include_router(listings.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(account.router)