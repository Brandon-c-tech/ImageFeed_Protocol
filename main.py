# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import os
from typing import Optional
from pydantic import BaseModel

# Create FastAPI application
app = FastAPI(
    title="ImageFeed",
    description="A simple image subscription service",
    version="0.1.0"
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/imagefeed")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Database Models
class Feed(Base):
    """
    Feed model represents a collection of images
    - id: Unique identifier for the feed
    - name: Display name of the feed
    - description: Optional description of the feed
    - created_at: Timestamp when the feed was created
    """
    __tablename__ = "feeds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Image(Base):
    """
    Image model represents an individual image in a feed
    - id: Unique identifier for the image
    - feed_id: Reference to the parent feed
    - filename: Original filename of the image
    - path: Storage path of the image on the server
    - created_at: Timestamp when the image was uploaded
    """
    __tablename__ = "images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feed_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response
class FeedCreate(BaseModel):
    """Schema for feed creation request"""
    name: str
    description: Optional[str] = None

class FeedResponse(BaseModel):
    """Schema for feed response"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Dependencies
def get_db():
    """Database session dependency"""
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

# API Routes
@app.post("/api/v1/feeds", response_model=FeedResponse)
def create_feed(feed: FeedCreate, db: Session = Depends(get_db)):
    """
    Create a new feed
    - Accepts feed name and optional description
    - Returns the created feed information
    """
    db_feed = Feed(name=feed.name, description=feed.description)
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed

@app.get("/api/v1/feeds/{feed_id}", response_model=FeedResponse)
def get_feed(feed_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Get feed information by ID
    - Returns feed details if found
    - Raises 404 if feed doesn't exist
    """
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    return feed

@app.post("/api/v1/feeds/{feed_id}/images")
async def upload_image(feed_id: uuid.UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload an image to a feed
    - Validates feed existence
    - Creates storage directory if needed
    - Saves image file and metadata
    - Returns image ID and success message
    """
    # Verify feed exists
    feed = db.query(Feed).filter(Feed.id == feed_id).first()
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")
    
    # Create upload directory
    upload_dir = f"uploads/{feed_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Save image metadata to database
    db_image = Image(
        feed_id=feed_id,
        filename=file.filename,
        path=file_path
    )
    db.add(db_image)
    db.commit()
    
    return JSONResponse(content={
        "message": "Image uploaded successfully",
        "image_id": str(db_image.id)
    })

@app.get("/api/v1/feeds/{feed_id}/images")
def list_images(feed_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    List all images in a feed
    - Returns array of image metadata
    - Each image contains ID and filename
    """
    images = db.query(Image).filter(Image.feed_id == feed_id).all()
    return [{"id": str(img.id), "filename": img.filename} for img in images]

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
