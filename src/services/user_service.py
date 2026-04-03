"""
User Management Service
"""
from sqlalchemy.orm import Session
from ..models.models import User, UserRole, UserStatus
from .token_service import TokenService
from ..models.schemas import UserCreate, UserUpdate, UserResponse
from fastapi import HTTPException, status

class UserService:
    """Service for user-related operations"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User creation data
        
        Returns:
            Created user
        
        Raises:
            HTTPException: If email already exists
        """
        # Check if email exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=TokenService.hash_password(user_data.password),
            role=UserRole(user_data.role),
            status=UserStatus.ACTIVE
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """
        Get user by email
        
        Args:
            db: Database session
            email: User email
        
        Returns:
            User or None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            User or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> tuple:
        """
        Get all users with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
        
        Returns:
            Tuple of (users list, total count)
        """
        total = db.query(User).count()
        users = db.query(User).offset(skip).limit(limit).all()
        return users, total
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information
        
        Args:
            db: Database session
            user_id: User ID to update
            user_data: Update data
        
        Returns:
            Updated user
        
        Raises:
            HTTPException: If user not found
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete a user
        
        Args:
            db: Database session
            user_id: User ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain password
        
        Returns:
            User if authentication successful
        
        Raises:
            HTTPException: If credentials invalid
        """
        user = UserService.get_user_by_email(db, email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not TokenService.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if user.status == UserStatus.INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
