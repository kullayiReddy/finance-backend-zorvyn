"""
Dashboard and Analytics Service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.models import FinancialRecord, RecordType
from ..models.schemas import DashboardSummary, CategorySummary, MonthlySummary, RecordResponse
from datetime import datetime, timedelta
from typing import List
from collections import defaultdict

class DashboardService:
    """Service for dashboard analytics"""
    
    @staticmethod
    def get_user_dashboard(db: Session, user_id: int) -> DashboardSummary:
        """
        Get complete dashboard summary for a user
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            Dashboard summary with all analytics
        """
        # Get all user records
        records = db.query(FinancialRecord).filter(
            FinancialRecord.user_id == user_id
        ).all()
        
        # Calculate totals
        total_income = sum(r.amount for r in records if r.type == RecordType.INCOME)
        total_expense = sum(r.amount for r in records if r.type == RecordType.EXPENSE)
        net_balance = total_income - total_expense
        
        # Get category-wise summary
        category_wise = DashboardService._get_category_summary(records)
        
        # Get monthly trends
        monthly_trends = DashboardService._get_monthly_trends(records)
        
        # Get recent records (last 10)
        recent_records = sorted(records, key=lambda x: x.date, reverse=True)[:10]
        
        return DashboardSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            category_wise=category_wise,
            monthly_trends=monthly_trends,
            recent_records=[RecordResponse.model_validate(r) for r in recent_records]
        )
    
    @staticmethod
    def _get_category_summary(records: List[FinancialRecord]) -> List[CategorySummary]:
        """
        Calculate category-wise summary
        
        Args:
            records: List of financial records
        
        Returns:
            List of category summaries
        """
        category_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for record in records:
            if record.type == RecordType.INCOME:
                category_data[record.category]["income"] += record.amount
            else:
                category_data[record.category]["expense"] += record.amount
        
        summaries = []
        for category, amounts in sorted(category_data.items()):
            net = amounts["income"] - amounts["expense"]
            summaries.append(
                CategorySummary(
                    category=category,
                    income=amounts["income"],
                    expense=amounts["expense"],
                    net=net
                )
            )
        
        return summaries
    
    @staticmethod
    def _get_monthly_trends(records: List[FinancialRecord]) -> List[MonthlySummary]:
        """
        Calculate monthly trends
        
        Args:
            records: List of financial records
        
        Returns:
            List of monthly summaries
        """
        monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for record in records:
            # Format: "2024-01"
            month_key = record.date.strftime("%Y-%m")
            
            if record.type == RecordType.INCOME:
                monthly_data[month_key]["income"] += record.amount
            else:
                monthly_data[month_key]["expense"] += record.amount
        
        summaries = []
        for month in sorted(monthly_data.keys()):
            amounts = monthly_data[month]
            net = amounts["income"] - amounts["expense"]
            summaries.append(
                MonthlySummary(
                    month=month,
                    income=amounts["income"],
                    expense=amounts["expense"],
                    net=net
                )
            )
        
        return summaries
    
    @staticmethod
    def get_total_income(db: Session, user_id: int) -> float:
        """Get total income for user"""
        result = db.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.user_id == user_id,
            FinancialRecord.type == RecordType.INCOME
        ).scalar()
        return float(result or 0)
    
    @staticmethod
    def get_total_expense(db: Session, user_id: int) -> float:
        """Get total expense for user"""
        result = db.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.user_id == user_id,
            FinancialRecord.type == RecordType.EXPENSE
        ).scalar()
        return float(result or 0)
    
    @staticmethod
    def get_balance(db: Session, user_id: int) -> float:
        """Get net balance for user"""
        income = DashboardService.get_total_income(db, user_id)
        expense = DashboardService.get_total_expense(db, user_id)
        return income - expense
    
    @staticmethod
    def get_monthly_summary(db: Session, user_id: int, year: int, month: int) -> dict:
        """
        Get summary for a specific month
        
        Args:
            db: Database session
            user_id: User ID
            year: Year (e.g., 2024)
            month: Month (1-12)
        
        Returns:
            Dictionary with income, expense, and net for the month
        """
        start_date = datetime(year, month, 1)
        
        # Get last day of month
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        income = db.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.user_id == user_id,
            FinancialRecord.type == RecordType.INCOME,
            FinancialRecord.date >= start_date,
            FinancialRecord.date <= end_date
        ).scalar()
        
        expense = db.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.user_id == user_id,
            FinancialRecord.type == RecordType.EXPENSE,
            FinancialRecord.date >= start_date,
            FinancialRecord.date <= end_date
        ).scalar()
        
        income = float(income or 0)
        expense = float(expense or 0)
        
        return {
            "month": f"{year:04d}-{month:02d}",
            "income": income,
            "expense": expense,
            "net": income - expense
        }
