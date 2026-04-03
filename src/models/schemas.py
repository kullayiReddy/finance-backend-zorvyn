"""
Pydantic schemas for request/response validation and documentation
"""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums for schemas
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class RecordTypeEnum(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    role: UserRoleEnum = Field(default=UserRoleEnum.VIEWER)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "full_name": "John Doe",
                "password": "securepass123",
                "role": "viewer"
            }
        }

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None

class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRoleEnum
    status: UserStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "viewer",
                "status": "active",
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }

# ============================================================================
# FINANCIAL RECORD SCHEMAS
# ============================================================================

class RecordBase(BaseModel):
    """Base record schema"""
    amount: float = Field(..., gt=0, description="Amount must be positive")
    type: RecordTypeEnum
    category: str = Field(..., min_length=1, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)

class RecordCreate(RecordBase):
    """Record creation schema"""
    date: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.50,
                "type": "income",
                "category": "Salary",
                "notes": "Monthly salary",
                "date": "2024-01-15T00:00:00"
            }
        }

class RecordUpdate(BaseModel):
    """Record update schema"""
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[RecordTypeEnum] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)

class RecordResponse(RecordBase):
    """Record response schema"""
    id: int
    user_id: int
    date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "amount": 100.50,
                "type": "income",
                "category": "Salary",
                "notes": "Monthly salary",
                "date": "2024-01-15T00:00:00",
                "created_at": "2024-01-15T10:30:00"
            }
        }

# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Number of records to return")

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[RecordResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "total": 50,
                "skip": 0,
                "limit": 10,
                "has_more": True
            }
        }

# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================

class CategorySummary(BaseModel):
    """Category-wise summary"""
    category: str
    income: float = Field(default=0, description="Total income in this category")
    expense: float = Field(default=0, description="Total expense in this category")
    net: float = Field(default=0, description="Net (income - expense)")

class MonthlySummary(BaseModel):
    """Monthly trends summary"""
    month: str  # Format: "2024-01"
    income: float
    expense: float
    net: float

class DashboardSummary(BaseModel):
    """Complete dashboard summary"""
    total_income: float
    total_expense: float
    net_balance: float
    category_wise: List[CategorySummary]
    monthly_trends: List[MonthlySummary]
    recent_records: List[RecordResponse] = Field(default=[], description="Last 10 records")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_income": 5000.00,
                "total_expense": 2000.00,
                "net_balance": 3000.00,
                "category_wise": [
                    {
                        "category": "Salary",
                        "income": 5000.00,
                        "expense": 0.00,
                        "net": 5000.00
                    }
                ],
                "monthly_trends": [
                    {
                        "month": "2024-01",
                        "income": 5000.00,
                        "expense": 2000.00,
                        "net": 3000.00
                    }
                ],
                "recent_records": []
            }
        }

# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    status_code: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "UNAUTHORIZED",
                "message": "Invalid credentials",
                "status_code": 401
            }
        }
