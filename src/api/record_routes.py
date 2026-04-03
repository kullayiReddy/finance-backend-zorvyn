"""
Financial Records Routes - CRUD with filtering and pagination
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..services.record_service import RecordService
from ..models.schemas import RecordResponse, RecordCreate, RecordUpdate, PaginatedResponse
from ..middleware.auth_middleware import CurrentUser, require_analyst_or_admin
from datetime import datetime

router = APIRouter(prefix="/api/v1/records", tags=["Financial Records"])

@router.post(
    "/",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create financial record",
    responses={
        201: {"description": "Record created"},
        401: {"description": "Not authenticated"}
    }
)
def create_record(
    record_data: RecordCreate,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Create a new financial record
    
    All authenticated users can create records for themselves
    """
    record = RecordService.create_record(
        db=db,
        user_id=current_user.user.id,
        record_data=record_data
    )
    
    return RecordResponse.model_validate(record)

@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List user's records",
    responses={
        200: {"description": "Records list"},
        401: {"description": "Not authenticated"}
    }
)
def list_records(
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(10, ge=1, le=100, description="Return N records"),
    category: str = Query(None, description="Filter by category"),
    type: str = Query(None, description="Filter by type (income/expense)"),
    search: str = Query(None, description="Search in notes"),
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get user's financial records with filtering and pagination
    
    Supports filtering by:
    - category: Exact category match
    - type: "income" or "expense"
    - search: Search in notes field
    """
    records, total = RecordService.get_user_records(
        db=db,
        user_id=current_user.user.id,
        skip=skip,
        limit=limit,
        category=category,
        record_type=type,
        search=search
    )
    
    has_more = (skip + limit) < total
    
    return PaginatedResponse(
        data=[RecordResponse.model_validate(r) for r in records],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more
    )

@router.get(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Get record by ID",
    responses={
        200: {"description": "Record details"},
        401: {"description": "Not authenticated"},
        404: {"description": "Record not found"}
    }
)
def get_record(
    record_id: int,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get a specific financial record
    
    Users can only view their own records
    """
    record = RecordService.get_record_by_id(db, record_id, current_user.user.id)
    return RecordResponse.model_validate(record)

@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Update record",
    responses={
        200: {"description": "Record updated"},
        401: {"description": "Not authenticated"},
        404: {"description": "Record not found"}
    }
)
def update_record(
    record_id: int,
    record_data: RecordUpdate,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Update a financial record
    
    Users can only update their own records
    """
    record = RecordService.update_record(
        db=db,
        record_id=record_id,
        user_id=current_user.user.id,
        record_data=record_data
    )
    
    return RecordResponse.model_validate(record)

@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete record",
    responses={
        204: {"description": "Record deleted"},
        401: {"description": "Not authenticated"},
        404: {"description": "Record not found"}
    }
)
def delete_record(
    record_id: int,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Delete a financial record
    
    Users can only delete their own records
    """
    RecordService.delete_record(db, record_id, current_user.user.id)
    return None

@router.get(
    "/filter/by-date-range",
    response_model=List[RecordResponse],
    summary="Get records by date range",
    responses={
        200: {"description": "Records in date range"},
        401: {"description": "Not authenticated"}
    }
)
def get_records_by_date_range(
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get records within a specific date range
    
    Example: /api/v1/records/filter/by-date-range?start_date=2024-01-01&end_date=2024-01-31
    """
    records = RecordService.get_user_records_by_date_range(
        db=db,
        user_id=current_user.user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return [RecordResponse.model_validate(r) for r in records]

@router.get(
    "/category/list",
    response_model=List[str],
    summary="Get user's categories",
    responses={
        200: {"description": "List of categories"},
        401: {"description": "Not authenticated"}
    }
)
def get_user_categories(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all unique categories used by the current user
    """
    from sqlalchemy import distinct
    
    categories = db.query(distinct(RecordService)).filter(
        RecordService.user_id == current_user.user.id
    ).all()
    
    # Fallback if query fails
    records = db.query(RecordService).filter(
        RecordService.user_id == current_user.user.id
    ).all()
    
    categories = sorted(set(r.category for r in records))
    return categories
