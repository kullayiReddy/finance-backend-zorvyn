"""
Authentication and Authorization Middleware
"""
from typing import Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.token_service import TokenService
from ..services.user_service import UserService
from ..models.models import UserRole, User

# Security scheme for Swagger UI
security = HTTPBearer()

class CurrentUser:
    """Dependency for getting current authenticated user"""
    
    def __init__(
        self,
        credentials: Any = Depends(security),
        db: Session = Depends(get_db)
    ):
        """
        Extract and validate JWT token from request
        
        Args:
            credentials: HTTP bearer token from Authorization header
            db: Database session
        """
        token = credentials.credentials
        
        try:
            payload = TokenService.verify_token(token)
            user_id: int = payload.get("user_id")
            email: str = payload.get("sub")
            
            if user_id is None or email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Fetch user from database
            user = UserService.get_user_by_id(db, user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            self.user = user
            self.db = db
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

def require_role(*roles: UserRole):
    """
    Decorator to require specific roles
    
    Usage:
        @app.get("/admin")
        def admin_endpoint(current_user: CurrentUser = Depends(require_role(UserRole.ADMIN))):
            ...
    
    Args:
        roles: Required user roles
    
    Returns:
        Dependency function
    """
    async def role_checker(current_user: CurrentUser = Depends()) -> CurrentUser:
        if current_user.user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    
    return role_checker

def require_admin(current_user: CurrentUser = Depends()) -> CurrentUser:
    """Quick dependency for admin-only endpoints"""
    if current_user.user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_analyst_or_admin(current_user: CurrentUser = Depends()) -> CurrentUser:
    """Quick dependency for analyst+ access"""
    if current_user.user.role not in [UserRole.ADMIN, UserRole.ANALYST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst access required"
        )
    return current_user
