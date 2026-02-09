from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import date
from app.db import get_db
from app.db.models import User
from app.schemas.seashell import SeashellCreate, SeashellResponse, SeashellUpdate, DeleteResponse
from app.core.security import verify_token
from app.services import SeashellService, SeashellNotFoundError

router = APIRouter(prefix="/api/v1/seashells", tags=["seashells"])


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
def create_seashell(
    seashell_data: SeashellCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Create a new seashell (requires authentication)."""
    token = extract_token(authorization)
    current_user = get_current_user(token=token, db=db)
    
    service = SeashellService(db)
    return service.create_seashell(seashell_data, added_by_id=current_user.id)


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
def update_seashell(
    seashell_id: UUID,
    seashell_data: SeashellUpdate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Update a seashell (requires authentication)."""
    token = extract_token(authorization)
    get_current_user(token=token, db=db)
    
    service = SeashellService(db)
    try:
        return service.update_seashell(seashell_id, seashell_data)
    except SeashellNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )


@router.delete("/{seashell_id}", response_model=DeleteResponse)
def delete_seashell(
    seashell_id: UUID,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Delete a seashell (requires authentication)."""
    token = extract_token(authorization)
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
