"""
User Management Routes - CRUD operations (Admin only)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.user_service import UserService
from ..models.schemas import UserResponse, UserCreate, UserUpdate, PaginatedResponse
from ..middleware.auth_middleware import CurrentUser, require_admin
from ..models.models import UserRole

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])

@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List all users",
    responses={
        200: {"description": "Users list"},
        403: {"description": "Admin access required"}
    }
)
def list_users(
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(10, ge=1, le=100, description="Return N records"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get list of all users (Admin only)
    
    Supports pagination with skip/limit parameters
    """
    users, total = UserService.get_all_users(db, skip=skip, limit=limit)
    has_more = (skip + limit) < total
    
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    responses={
        200: {"description": "User details"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"}
    }
)
def get_user(
    user_id: int,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get a user's details
    
    - Admins can view any user
    - Users can only view themselves
    """
    # Check permissions
    if current_user.user.role != UserRole.ADMIN and current_user.user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other users' details"
        )
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    responses={
        201: {"description": "User created"},
        400: {"description": "Email already exists"},
        403: {"description": "Admin access required"}
    }
)
def create_user(
    user_data: UserCreate,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only)
    
    Admin can set the user's role directly
    """
    user = UserService.create_user(db, user_data)
    return UserResponse.model_validate(user)

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    responses={
        200: {"description": "User updated"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"}
    }
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Update user information
    
    - Admins can update any user
    - Users can only update their own name
    - Only admins can change roles and status
    """
    # Check permissions
    if current_user.user.role != UserRole.ADMIN:
        # Non-admin can only update themselves and only their name
        if current_user.user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other users"
            )
        
        # Non-admin cannot change role or status
        if user_data.role is not None or user_data.status is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change role and status"
            )
    
    user = UserService.update_user(db, user_id, user_data)
    return UserResponse.model_validate(user)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    responses={
        204: {"description": "User deleted"},
        403: {"description": "Admin access required"},
        404: {"description": "User not found"}
    }
)
def delete_user(
    user_id: int,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (Admin only)
    
    Also deletes all their financial records
    """
    UserService.delete_user(db, user_id)
    return None

@router.get(
    "/search/email",
    response_model=UserResponse,
    summary="Search user by email",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"}
    }
)
def search_user_by_email(
    email: str = Query(..., description="User email"),
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Search for a user by email (Admin only)
    """
    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)
