"""
User service - handles business logic for user operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserTypeEnum
from app.schemas.user import UserCreate, UserUpdate
from app.security.auth import hash_password, verify_password
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user-related operations."""

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_create: User creation schema

        Returns:
            Created user object
        """
        try:
            hashed_password = hash_password(user_create.password)
            
            db_user = User(
                name=user_create.name,
                email=user_create.email,
                hashed_password=hashed_password,
                user_type=user_create.user_type,
                institution=user_create.institution,
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created: {db_user.email}")
            return db_user
        except IntegrityError:
            db.rollback()
            logger.error(f"User already exists: {user_create.email}")
            raise ValueError("Email already registered")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User | None:
        """
        Authenticate user by email and password.

        Args:
            db: Database session
            email: User email
            password: Plain password

        Returns:
            User if authenticated, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_update: UserUpdate
    ) -> User | None:
        """Update user profile."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        
        logger.info(f"User updated: {user.email}")
        return user

    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """Deactivate a user account."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        user.is_active = False
        db.commit()
        
        logger.info(f"User deactivated: {user.email}")
        return True

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user account (cascade delete)."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False

        db.delete(user)
        db.commit()
        
        logger.info(f"User deleted: {user.email}")
        return True
