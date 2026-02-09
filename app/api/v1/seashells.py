from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from app.db import get_db
from app.db.models import Seashell, User
from app.schemas.seashell import SeashellCreate, SeashellResponse
from app.core.security import verify_token

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


@router.post("/create", response_model=SeashellResponse)
def create_seashell(
    seashell_data: SeashellCreate,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
):
    """Create a new seashell (requires authentication)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    token = authorization.replace("Bearer ", "")
    current_user = get_current_user(token=token, db=db)
    
    new_seashell = Seashell(
        name=seashell_data.name,
        species=seashell_data.species,
        description=seashell_data.description,
        color=seashell_data.color,
        size_mm=seashell_data.size_mm,
        found_on=seashell_data.found_on,
        found_at=seashell_data.found_at,
        storage_location=seashell_data.storage_location,
        condition=seashell_data.condition,
        notes=seashell_data.notes,
        image_url=seashell_data.image_url,
    )
    
    db.add(new_seashell)
    db.commit()
    db.refresh(new_seashell)
    
    return new_seashell


@router.get("/", response_model=List[SeashellResponse])
def list_seashells(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    """List all seashells with pagination."""
    seashells = db.query(Seashell).offset(skip).limit(limit).all()
    return seashells


@router.get("/{seashell_id}", response_model=SeashellResponse)
def get_seashell(
    seashell_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a seashell by ID."""
    seashell = db.query(Seashell).filter(Seashell.id == seashell_id).first()
    if not seashell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seashell not found",
        )
    return seashell
