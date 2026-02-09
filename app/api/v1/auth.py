from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.user import UserLogin, TokenResponse
from app.services import UserService, InvalidCredentialsError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token."""
    service = UserService(db)
    try:
        return service.authenticate(user_data.email, user_data.password)
    except InvalidCredentialsError as e:
        # Check if it's an inactive account (different HTTP status)
        if "inactive" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
