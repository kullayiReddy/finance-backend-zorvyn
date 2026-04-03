"""
Financial Record Management Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.models import FinancialRecord, RecordType
from ..models.schemas import RecordCreate, RecordUpdate, RecordResponse
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Tuple

class RecordService:
    """Service for financial record operations"""
    
    @staticmethod
    def create_record(db: Session, user_id: int, record_data: RecordCreate) -> FinancialRecord:
        """
        Create a new financial record
        
        Args:
            db: Database session
            user_id: User ID who owns the record
            record_data: Record data
        
        Returns:
            Created record
        """
        db_record = FinancialRecord(
            user_id=user_id,
            amount=record_data.amount,
            type=RecordType(record_data.type),
            category=record_data.category,
            date=record_data.date or datetime.utcnow(),
            notes=record_data.notes
        )
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record
    
    @staticmethod
    def get_record_by_id(db: Session, record_id: int, user_id: int) -> FinancialRecord:
        """
        Get a specific record by ID (only own records)
        
        Args:
            db: Database session
            record_id: Record ID
            user_id: User ID (for permission check)
        
        Returns:
            Record or None
        
        Raises:
            HTTPException: If record not found or not owned by user
        """
        record = db.query(FinancialRecord).filter(
            FinancialRecord.id == record_id,
            FinancialRecord.user_id == user_id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        return record
    
    @staticmethod
    def get_user_records(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        category: str = None,
        record_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        search: str = None
    ) -> Tuple[List[FinancialRecord], int]:
        """
        Get user's records with filtering and pagination
        
        Args:
            db: Database session
            user_id: User ID
            skip: Records to skip
            limit: Records to return
            category: Filter by category
            record_type: Filter by type (income/expense)
            start_date: Filter from date
            end_date: Filter to date
            search: Search in notes
        
        Returns:
            Tuple of (records list, total count)
        """
        query = db.query(FinancialRecord).filter(FinancialRecord.user_id == user_id)
        
        # Apply filters
        if category:
            query = query.filter(FinancialRecord.category == category)
        
        if record_type:
            query = query.filter(FinancialRecord.type == RecordType(record_type))
        
        if start_date:
            query = query.filter(FinancialRecord.date >= start_date)
        
        if end_date:
            query = query.filter(FinancialRecord.date <= end_date)
        
        if search:
            query = query.filter(FinancialRecord.notes.ilike(f"%{search}%"))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and sort by date descending
        records = query.order_by(FinancialRecord.date.desc()).offset(skip).limit(limit).all()
        
        return records, total
    
    @staticmethod
    def update_record(
        db: Session,
        record_id: int,
        user_id: int,
        record_data: RecordUpdate
    ) -> FinancialRecord:
        """
        Update a financial record
        
        Args:
            db: Database session
            record_id: Record ID
            user_id: User ID (for permission check)
            record_data: Update data
        
        Returns:
            Updated record
        
        Raises:
            HTTPException: If record not found
        """
        db_record = RecordService.get_record_by_id(db, record_id, user_id)
        
        # Update only provided fields
        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_record, field, value)
        
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record
    
    @staticmethod
    def delete_record(db: Session, record_id: int, user_id: int) -> bool:
        """
        Delete a financial record
        
        Args:
            db: Database session
            record_id: Record ID
            user_id: User ID (for permission check)
        
        Returns:
            True if deleted
        
        Raises:
            HTTPException: If record not found
        """
        db_record = RecordService.get_record_by_id(db, record_id, user_id)
        
        db.delete(db_record)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_records_by_date_range(
        db: Session,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[FinancialRecord]:
        """
        Get user records within a date range
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Start date
            end_date: End date
        
        Returns:
            List of records
        """
        return db.query(FinancialRecord).filter(
            and_(
                FinancialRecord.user_id == user_id,
                FinancialRecord.date >= start_date,
                FinancialRecord.date <= end_date
            )
        ).order_by(FinancialRecord.date.desc()).all()
