"""
Unit tests for authentication module.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserTypeEnum
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.security.auth import hash_password, verify_password


@pytest.fixture
def test_user_data():
    """Create test user data."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123",
        "user_type": UserTypeEnum.STUDENT,
        "institution": "Test University"
    }


def test_password_hashing():
    """Test password hashing and verification."""
    plain_password = "mysecurepassword123"
    hashed = hash_password(plain_password)
    
    assert hashed != plain_password
    assert verify_password(plain_password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_user(db: Session, test_user_data):
    """Test user creation."""
    user_create = UserCreate(**test_user_data)
    user = UserService.create_user(db, user_create)
    
    assert user.id is not None
    assert user.email == test_user_data["email"]
    assert user.name == test_user_data["name"]
    assert user.user_type == test_user_data["user_type"]


def test_get_user_by_email(db: Session, test_user_data):
    """Test retrieving user by email."""
    user_create = UserCreate(**test_user_data)
    created_user = UserService.create_user(db, user_create)
    
    found_user = UserService.get_user_by_email(db, test_user_data["email"])
    
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == test_user_data["email"]


def test_authenticate_user(db: Session, test_user_data):
    """Test user authentication."""
    user_create = UserCreate(**test_user_data)
    UserService.create_user(db, user_create)
    
    # Correct password
    authenticated_user = UserService.authenticate_user(
        db,
        test_user_data["email"],
        test_user_data["password"]
    )
    assert authenticated_user is not None
    
    # Wrong password
    wrong_auth = UserService.authenticate_user(
        db,
        test_user_data["email"],
        "wrongpassword"
    )
    assert wrong_auth is None
