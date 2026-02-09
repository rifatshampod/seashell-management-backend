"""
User Service - Business logic layer for user operations.
Handles user registration, authentication, and profile management.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token


class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass


class UserAlreadyExistsError(UserServiceError):
    """Raised when attempting to create a user with an existing email."""
    pass


class UserNotFoundError(UserServiceError):
    """Raised when a user is not found."""
    pass


class InvalidCredentialsError(UserServiceError):
    """Raised when login credentials are invalid."""
    pass


class UserService:
    """Service class for user-related business logic."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data containing email, password, and optional full_name.
            
        Returns:
            The created User object.
            
        Raises:
            UserAlreadyExistsError: If a user with the given email already exists.
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

        # Create new user with hashed password
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

    def authenticate(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate a user and return an access token.
        
        Args:
            email: User's email address.
            password: User's password.
            
        Returns:
            TokenResponse containing access_token and token_type.
            
        Raises:
            InvalidCredentialsError: If email or password is invalid.
        """
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User account is inactive")

        # Generate access token
        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token)

    def get_user_by_id(self, user_id: UUID) -> User:
        """
        Get a user by their ID.
        
        Args:
            user_id: The UUID of the user.
            
        Returns:
            The User object.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by their email address.
        
        Args:
            email: The user's email address.
            
        Returns:
            The User object or None if not found.
        """
        return self.db.query(User).filter(User.email == email).first()

    def update_user(self, user_id: UUID, full_name: Optional[str] = None) -> User:
        """
        Update user profile information.
        
        Args:
            user_id: The UUID of the user to update.
            full_name: New full name (optional).
            
        Returns:
            The updated User object.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_user_by_id(user_id)

        if full_name is not None:
            user.full_name = full_name

        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user_id: UUID, new_password: str) -> User:
        """
        Change a user's password.
        
        Args:
            user_id: The UUID of the user.
            new_password: The new password to set.
            
        Returns:
            The updated User object.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_user_by_id(user_id)
        user.password_hash = hash_password(new_password)

        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate a user account.
        
        Args:
            user_id: The UUID of the user to deactivate.
            
        Returns:
            The updated User object.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_user_by_id(user_id)
        user.is_active = False

        self.db.commit()
        self.db.refresh(user)
        return user

    def activate_user(self, user_id: UUID) -> User:
        """
        Activate a user account.
        
        Args:
            user_id: The UUID of the user to activate.
            
        Returns:
            The updated User object.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_user_by_id(user_id)
        user.is_active = True

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: UUID) -> None:
        """
        Permanently delete a user account.
        
        Args:
            user_id: The UUID of the user to delete.
            
        Raises:
            UserNotFoundError: If the user is not found.
        """
        user = self.get_user_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
