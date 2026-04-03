"""
Authentication Routes - Login, Token Refresh, Logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.user_service import UserService
from ..services.token_service import TokenService
from ..models.schemas import LoginRequest, TokenResponse, RefreshTokenRequest, UserCreate
from ..middleware.auth_middleware import CurrentUser
from jose import JWTError

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Email already exists"}
    }
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    
    - Email must be unique
    - Password must be at least 6 characters
    - Returns JWT tokens for immediate login
    """
    user = UserService.create_user(db, user_data)
    
    tokens = TokenService.create_tokens(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"]
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        403: {"description": "User account inactive"}
    }
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password
    
    Returns JWT access and refresh tokens for use in subsequent requests
    """
    user = UserService.authenticate_user(db, credentials.email, credentials.password)
    
    tokens = TokenService.create_tokens(
        user_id=user.id,
        email=user.email,
        role=user.role.value
    )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=tokens["expires_in"]
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid refresh token"}
    }
)
def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Get a new access token using a refresh token
    
    Refresh tokens have a longer expiration (7 days vs 30 minutes)
    """
    try:
        payload = TokenService.verify_token(request.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise JWTError("Not a refresh token")
        
        user_id = payload.get("user_id")
        email = payload.get("sub")
        
        # Verify user still exists
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        tokens = TokenService.create_tokens(
            user_id=user.id,
            email=user.email,
            role=user.role.value
        )
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            expires_in=tokens["expires_in"]
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    responses={
        204: {"description": "Logout successful"},
        401: {"description": "Not authenticated"}
    }
)
def logout(current_user: CurrentUser = Depends()):
    """
    Logout current user (stateless - just invalidate client-side token)
    
    Since we use stateless JWT tokens, logout is handled client-side
    by discarding the tokens. This endpoint confirms user identity.
    """
    # Stateless - token is discarded client-side
    # In production, you might want to add token blacklisting
    return None

@router.get(
    "/me",
    summary="Get current user info",
    responses={
        200: {"description": "Current user information"},
        401: {"description": "Not authenticated"}
    }
)
def get_current_user_info(current_user: CurrentUser = Depends()):
    """
    Get information about the currently authenticated user
    """
    return {
        "id": current_user.user.id,
        "email": current_user.user.email,
        "full_name": current_user.user.full_name,
        "role": current_user.user.role.value,
        "status": current_user.user.status.value
    }
