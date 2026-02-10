from fastapi import APIRouter, Depends, HTTPException, status, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db import get_db
from app.db.models import User
from app.schemas.user import UserResponse, PasswordReset, UserCreate
from app.core.security import verify_token
from app.services import UserService, UserNotFoundError, UserAlreadyExistsError

router = APIRouter(prefix="/api/v1/users", tags=["users"])

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
    
    service = UserService(db)
    try:
        return service.get_user_by_id(UUID(user_id))
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


def extract_token(authorization: Optional[str]) -> str:
    """Extract and validate Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return authorization.replace("Bearer ", "")


@router.get("/profile", response_model=UserResponse)
def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Get current logged-in user info."""
    token = credentials.credentials
    return get_current_user(token=token, db=db)


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """List all users."""
    users = db.query(User).all()
    return users


@router.post("/create-user", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """Create a new user (requires authentication)."""
    token = credentials.credentials
    get_current_user(token=token, db=db)
    
    service = UserService(db)
    try:
        return service.create_user(user_data)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Get user by ID."""
    service = UserService(db)
    try:
        return service.get_user_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: UUID, db: Session = Depends(get_db)):
    """Activate a user account."""
    service = UserService(db)
    try:
        return service.activate_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: UUID, db: Session = Depends(get_db)):
    """Deactivate a user account."""
    service = UserService(db)
    try:
        return service.deactivate_user(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_password(user_id: UUID, password_data: PasswordReset, db: Session = Depends(get_db)):
    """Reset user password."""
    service = UserService(db)
    try:
        return service.change_password(user_id, password_data.new_password)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
