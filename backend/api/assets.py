"""
Asset management API endpoints for handling images, fonts, and icons.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
import shutil
from pathlib import Path
from PIL import Image
import io

router = APIRouter()

# Asset storage configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class AssetResponse(BaseModel):
    """Asset response model."""
    id: str
    filename: str
    original_filename: str
    url: str
    size: int
    width: Optional[int] = None
    height: Optional[int] = None
    format: str
    optimized: bool = False
    created_at: str


class AssetListResponse(BaseModel):
    """Asset list response."""
    assets: List[AssetResponse]
    total: int


class UnsplashPhoto(BaseModel):
    """Unsplash photo model."""
    id: str
    description: Optional[str]
    urls: dict
    user: dict
    width: int
    height: int


class UnsplashSearchResponse(BaseModel):
    """Unsplash search response."""
    results: List[UnsplashPhoto]
    total: int


class GoogleFont(BaseModel):
    """Google Font model."""
    family: str
    variants: List[str]
    subsets: List[str]
    category: str


class GoogleFontsResponse(BaseModel):
    """Google Fonts response."""
    fonts: List[GoogleFont]
    total: int


def optimize_image(image_path: Path, max_width: int = 1920) -> Path:
    """
    Optimize an image by resizing and converting to WebP.
    
    Args:
        image_path: Path to the original image
        max_width: Maximum width for the optimized image
        
    Returns:
        Path to the optimized image
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for WebP)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as WebP
            optimized_path = image_path.with_suffix('.webp')
            img.save(optimized_path, 'WEBP', quality=85, optimize=True)
            
            return optimized_path
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return image_path


@router.post("/assets/upload", response_model=AssetResponse)
async def upload_asset(
    file: UploadFile = File(...),
    optimize: bool = Query(True, description="Optimize image (resize and convert to WebP)"),
):
    """
    Upload an asset (image, icon, etc.).
    
    - **file**: The file to upload
    - **optimize**: Whether to optimize the image (default: True)
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / filename
    
    # Save uploaded file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Validate file size
    if file_size > MAX_FILE_SIZE:
        file_path.unlink()  # Delete the file
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Get image dimensions
    width, height = None, None
    optimized = False
    
    if file_ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        try:
            with Image.open(file_path) as img:
                width, height = img.size
            
            # Optimize if requested
            if optimize and file_ext != ".svg":
                optimized_path = optimize_image(file_path)
                if optimized_path != file_path:
                    # Remove original and use optimized
                    file_path.unlink()
                    file_path = optimized_path
                    filename = optimized_path.name
                    file_size = optimized_path.stat().st_size
                    optimized = True
                    
                    # Update dimensions
                    with Image.open(file_path) as img:
                        width, height = img.size
        except Exception as e:
            print(f"Error processing image: {e}")
    
    return AssetResponse(
        id=file_id,
        filename=filename,
        original_filename=file.filename,
        url=f"/api/assets/{filename}",
        size=file_size,
        width=width,
        height=height,
        format=file_ext.lstrip('.'),
        optimized=optimized,
        created_at="2024-01-01T00:00:00Z",  # TODO: Use actual timestamp
    )


@router.get("/assets/{filename}")
async def get_asset(filename: str):
    """
    Get an uploaded asset by filename.
    
    - **filename**: The filename of the asset
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return FileResponse(file_path)


@router.get("/assets", response_model=AssetListResponse)
async def list_assets():
    """
    List all uploaded assets.
    """
    assets = []
    
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            file_ext = file_path.suffix.lower()
            if file_ext in SUPPORTED_IMAGE_FORMATS:
                file_size = file_path.stat().st_size
                width, height = None, None
                
                if file_ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                    except:
                        pass
                
                assets.append(AssetResponse(
                    id=file_path.stem,
                    filename=file_path.name,
                    original_filename=file_path.name,
                    url=f"/api/assets/{file_path.name}",
                    size=file_size,
                    width=width,
                    height=height,
                    format=file_ext.lstrip('.'),
                    optimized=file_ext == ".webp",
                    created_at="2024-01-01T00:00:00Z",
                ))
    
    return AssetListResponse(
        assets=assets,
        total=len(assets),
    )


@router.delete("/assets/{filename}")
async def delete_asset(filename: str):
    """
    Delete an uploaded asset.
    
    - **filename**: The filename of the asset to delete
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    
    try:
        file_path.unlink()
        return {"message": "Asset deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete asset: {str(e)}")


# Unsplash Integration
@router.get("/assets/unsplash/search", response_model=UnsplashSearchResponse)
async def search_unsplash(
    query: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=30, description="Results per page"),
):
    """
    Search for photos on Unsplash.
    
    - **query**: Search query
    - **page**: Page number (default: 1)
    - **per_page**: Results per page (default: 20, max: 30)
    """
    # TODO: Implement actual Unsplash API integration
    # For now, return mock data
    return UnsplashSearchResponse(
        results=[
            UnsplashPhoto(
                id="mock-1",
                description="Beautiful landscape",
                urls={
                    "raw": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
                    "full": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920",
                    "regular": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080",
                    "small": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400",
                    "thumb": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200",
                },
                user={
                    "name": "John Doe",
                    "username": "johndoe",
                },
                width=4000,
                height=3000,
            )
        ],
        total=1,
    )


# Google Fonts Integration
@router.get("/assets/fonts", response_model=GoogleFontsResponse)
async def list_google_fonts(
    search: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Font category"),
):
    """
    List Google Fonts.
    
    - **search**: Optional search query
    - **category**: Optional category filter (serif, sans-serif, display, handwriting, monospace)
    """
    # Popular Google Fonts
    fonts = [
        GoogleFont(
            family="Inter",
            variants=["100", "200", "300", "regular", "500", "600", "700", "800", "900"],
            subsets=["latin", "latin-ext"],
            category="sans-serif",
        ),
        GoogleFont(
            family="Roboto",
            variants=["100", "300", "regular", "500", "700", "900"],
            subsets=["latin", "latin-ext"],
            category="sans-serif",
        ),
        GoogleFont(
            family="Open Sans",
            variants=["300", "regular", "500", "600", "700", "800"],
            subsets=["latin", "latin-ext"],
            category="sans-serif",
        ),
        GoogleFont(
            family="Montserrat",
            variants=["100", "200", "300", "regular", "500", "600", "700", "800", "900"],
            subsets=["latin", "latin-ext"],
            category="sans-serif",
        ),
        GoogleFont(
            family="Poppins",
            variants=["100", "200", "300", "regular", "500", "600", "700", "800", "900"],
            subsets=["latin", "latin-ext"],
            category="sans-serif",
        ),
        GoogleFont(
            family="Playfair Display",
            variants=["regular", "500", "600", "700", "800", "900"],
            subsets=["latin", "latin-ext"],
            category="serif",
        ),
        GoogleFont(
            family="Lora",
            variants=["regular", "500", "600", "700"],
            subsets=["latin", "latin-ext"],
            category="serif",
        ),
    ]
    
    # Filter by search query
    if search:
        search_lower = search.lower()
        fonts = [f for f in fonts if search_lower in f.family.lower()]
    
    # Filter by category
    if category:
        fonts = [f for f in fonts if f.category == category]
    
    return GoogleFontsResponse(
        fonts=fonts,
        total=len(fonts),
    )
