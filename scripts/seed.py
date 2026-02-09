"""Seed script to create initial test user."""
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.db.models import User

settings = get_settings()


def seed_initial_user():
    """Create initial test user."""
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "test@seashell.com").first()
    if existing_user:
        print("Test user already exists!")
        db.close()
        return
    
    # Create initial test user
    test_user = User(
        email="test@seashell.com",
        password_hash=hash_password("password123"),
        full_name="Test User",
        is_active=True,
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"  Test user created successfully!")
    print(f"  Email: test@seashell.com")
    print(f"  Password: password123")
    print(f"  User ID: {test_user.id}")
    
    db.close()


if __name__ == "__main__":
    seed_initial_user()
