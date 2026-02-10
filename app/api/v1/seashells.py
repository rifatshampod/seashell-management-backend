from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, Form, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date
from app.db import get_db
from app.db.models import User
from app.schemas.seashell import SeashellCreate, SeashellResponse, SeashellUpdate, DeleteResponse
from app.core.security import verify_token
from app.services import SeashellService, SeashellNotFoundError
from app.core.file_upload import save_upload_file, InvalidFileTypeError, FileTooLargeError
    

router = APIRouter(prefix="/api/v1/seashells", tags=["seashells"])

# Security scheme for Swagger UI
security = HTTPBearer()


def get_current_user(token: str = None, db: Session = Depends(get_db)) -> User:
    """Extract user from JWT token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


def extract_token(authorization: Optional[str]) -> str:
    """Extract and validate Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return authorization.replace("Bearer ", "")


@router.post("/create", response_model=SeashellResponse)
async def create_seashell(
    name: str = Form(...),
    species: str = Form(...),
    description: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    size_mm: Optional[int] = Form(None),
    found_on: Optional[date] = Form(None),
    found_at: Optional[str] = Form(None),
    storage_location: Optional[str] = Form(None),
    condition: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Create a new seashell with optional image in a single request (requires authentication)."""
    # Authenticate user using the Bearer token from Security
    token = credentials.credentials
    current_user = get_current_user(token=token, db=db)
    
    # Create seashell data object from form fields
    seashell_data = SeashellCreate(
        name=name,
        species=species,
        description=description,
        color=color,
        size_mm=size_mm,
        found_on=found_on,
        found_at=found_at,
        storage_location=storage_location,
        condition=condition,
        notes=notes,
    )
    
    # Delegate to service layer
    service = SeashellService(db)
    try:
        return await service.create_seashell_with_image(
            seashell_data, added_by_id=current_user.id, file=file
        )
    except InvalidFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}",
        )


@router.get("/", response_model=List[SeashellResponse])
def list_seashells(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    species: Optional[str] = None,
    color: Optional[str] = None,
    condition: Optional[str] = None,
    storage_location: Optional[str] = None,
    min_size_mm: Optional[int] = None,
    max_size_mm: Optional[int] = None,
    found_after: Optional[date] = None,
    found_before: Optional[date] = None,
    search: Optional[str] = None,
):
    """List all seashells with optional filtering and pagination."""
    service = SeashellService(db)
    return service.get_all_seashells(
        skip=skip,
        limit=limit,
        species=species,
        color=color,
        condition=condition,
        storage_location=storage_location,
        min_size_mm=min_size_mm,
        max_size_mm=max_size_mm,
        found_after=found_after,
        found_before=found_before,
        search=search,
    )


@router.get("/filters/species", response_model=List[str])
def get_unique_species(db: Session = Depends(get_db)):
    """Get all unique species values for filtering."""
    service = SeashellService(db)
    return service.get_unique_species()


@router.get("/filters/colors", response_model=List[str])
def get_unique_colors(db: Session = Depends(get_db)):
    """Get all unique color values for filtering."""
    service = SeashellService(db)
    return service.get_unique_colors()


@router.get("/filters/conditions", response_model=List[str])
def get_unique_conditions(db: Session = Depends(get_db)):
    """Get all unique condition values for filtering."""
    service = SeashellService(db)
    return service.get_unique_conditions()


@router.get("/filters/locations", response_model=List[str])
def get_unique_locations(db: Session = Depends(get_db)):
    """Get all unique storage location values for filtering."""
    service = SeashellService(db)
    return service.get_unique_storage_locations()


@router.get("/{seashell_id}", response_model=SeashellResponse)
def get_seashell(
    seashell_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a seashell by ID."""
    service = SeashellService(db)
    try:
        return service.get_seashell_by_id(seashell_id)
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )


@router.patch("/{seashell_id}", response_model=SeashellResponse)
async def update_seashell(
    seashell_id: UUID,
    name: Optional[str] = Form(None),
    species: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    size_mm: Optional[int] = Form(None),
    found_on: Optional[date] = Form(None),
    found_at: Optional[str] = Form(None),
    storage_location: Optional[str] = Form(None),
    condition: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Update a seashell with optional image in a single request (requires authentication)."""
    # Authenticate user using the Bearer token from Security
    token = credentials.credentials
    get_current_user(token=token, db=db)
    
    # Create update data object from form fields
    seashell_data = SeashellUpdate(
        name=name,
        species=species,
        description=description,
        color=color,
        size_mm=size_mm,
        found_on=found_on,
        found_at=found_at,
        storage_location=storage_location,
        condition=condition,
        notes=notes,
    )
    
    # Delegate to service layer
    service = SeashellService(db)
    try:
        return await service.update_seashell_with_image(
            seashell_id, seashell_data, file=file
        )
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )
    except InvalidFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}",
        )


@router.delete("/{seashell_id}", response_model=DeleteResponse)
def delete_seashell(
    seashell_id: UUID,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Delete a seashell (requires authentication)."""
    token = credentials.credentials
    get_current_user(token=token, db=db)
    
    service = SeashellService(db)
    try:
        service.delete_seashell(seashell_id)
        return {"message": "Seashell deleted successfully", "id": seashell_id}
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )


@router.post("/{seashell_id}/upload-image", response_model=SeashellResponse)
async def upload_image(
    seashell_id: UUID,
    file: UploadFile,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Upload an image for a seashell (requires authentication)."""
    token = credentials.credentials
    get_current_user(token=token, db=db)
    
    service = SeashellService(db)
    
    # Verify seashell exists
    try:
        service.get_seashell_by_id(seashell_id)
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )
    
    # Save the file
    try:
        image_url = await save_upload_file(file, str(seashell_id))
    except InvalidFileTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except FileTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        )
    
    # Update database with image URL
    return service.update_image_url(seashell_id, image_url)


@router.delete("/{seashell_id}/image", response_model=SeashellResponse)
def delete_image(
    seashell_id: UUID,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Delete the image for a seashell (requires authentication)."""
    token = credentials.credentials
    get_current_user(token=token, db=db)
    
    service = SeashellService(db)
    try:
        return service.delete_image(seashell_id)
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )

