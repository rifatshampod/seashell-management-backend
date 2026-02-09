"""
File upload utilities for handling file storage operations.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status


# Configuration
UPLOAD_DIR = Path("uploads/seashells")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileUploadError(Exception):
    """Base exception for file upload errors."""
    pass


class InvalidFileTypeError(FileUploadError):
    """Raised when file type is not allowed."""
    pass


class FileTooLargeError(FileUploadError):
    """Raised when file exceeds size limit."""
    pass


def ensure_upload_directory() -> None:
    """Create upload directory if it doesn't exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension and return it.
    
    Args:
        filename: Original filename.
        
    Returns:
        File extension (lowercase).
        
    Raises:
        InvalidFileTypeError: If file type is not allowed.
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileTypeError(
            f"File type '{ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving extension.
    
    Args:
        original_filename: Original filename.
        
    Returns:
        Unique filename with UUID prefix.
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    return f"{unique_id}{ext}"


async def save_upload_file(
    file: UploadFile,
    seashell_id: str,
) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        file: The uploaded file.
        seashell_id: UUID of the seashell (used in path).
        
    Returns:
        The URL path to access the file.
        
    Raises:
        InvalidFileTypeError: If file type is not allowed.
        FileTooLargeError: If file exceeds size limit.
    """
    # Validate file type
    ext = validate_file_extension(file.filename or "unknown.jpg")
    
    # Check file size by reading content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise FileTooLargeError(
            f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB"
        )
    
    # Create directory structure
    seashell_dir = UPLOAD_DIR / str(seashell_id)
    seashell_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    filename = generate_unique_filename(file.filename or f"image{ext}")
    file_path = seashell_dir / filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return URL path
    return f"/uploads/seashells/{seashell_id}/{filename}"


def delete_seashell_images(seashell_id: str) -> None:
    """
    Delete all images for a seashell.
    
    Args:
        seashell_id: UUID of the seashell.
    """
    seashell_dir = UPLOAD_DIR / str(seashell_id)
    if seashell_dir.exists():
        shutil.rmtree(seashell_dir)


def delete_image_file(image_url: str) -> bool:
    """
    Delete a specific image file.
    
    Args:
        image_url: URL path of the image.
        
    Returns:
        True if deleted, False if not found.
    """
    if not image_url or not image_url.startswith("/uploads/seashells/"):
        return False
    
    # Convert URL path to file path
    relative_path = image_url.replace("/uploads/seashells/", "")
    file_path = UPLOAD_DIR / relative_path
    
    if file_path.exists():
        file_path.unlink()
        return True
    return False
