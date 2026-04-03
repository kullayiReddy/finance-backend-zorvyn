"""
Dashboard and Analytics Routes
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.dashboard_service import DashboardService
from ..models.schemas import DashboardSummary
from ..middleware.auth_middleware import CurrentUser, require_analyst_or_admin
from ..models.models import UserRole

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard & Analytics"])

@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get dashboard summary",
    responses={
        200: {"description": "Complete dashboard data"},
        401: {"description": "Not authenticated"}
    }
)
def get_dashboard_summary(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard summary with all analytics
    
    Returns:
    - Total income and expense
    - Net balance
    - Category-wise breakdown
    - Monthly trends (all months)
    - Recent 10 records
    
    All authenticated users can access their own dashboard
    """
    dashboard = DashboardService.get_user_dashboard(db, current_user.user.id)
    return dashboard

@router.get(
    "/total-income",
    response_model=dict,
    summary="Get total income",
    responses={
        200: {"description": "Total income amount"},
        401: {"description": "Not authenticated"}
    }
)
def get_total_income(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get user's total income across all records
    """
    total = DashboardService.get_total_income(db, current_user.user.id)
    return {
        "total_income": total,
        "currency": "USD"
    }

@router.get(
    "/total-expense",
    response_model=dict,
    summary="Get total expense",
    responses={
        200: {"description": "Total expense amount"},
        401: {"description": "Not authenticated"}
    }
)
def get_total_expense(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get user's total expense across all records
    """
    total = DashboardService.get_total_expense(db, current_user.user.id)
    return {
        "total_expense": total,
        "currency": "USD"
    }

@router.get(
    "/net-balance",
    response_model=dict,
    summary="Get net balance",
    responses={
        200: {"description": "Net balance (income - expense)"},
        401: {"description": "Not authenticated"}
    }
)
def get_net_balance(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get user's net balance (total income - total expense)
    """
    balance = DashboardService.get_balance(db, current_user.user.id)
    return {
        "net_balance": balance,
        "currency": "USD"
    }

@router.get(
    "/monthly/{year}/{month}",
    response_model=dict,
    summary="Get monthly summary",
    responses={
        200: {"description": "Monthly summary data"},
        401: {"description": "Not authenticated"}
    }
)
def get_monthly_summary(
    year: int,
    month: int,
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get summary for a specific month
    
    Path parameters:
    - year: e.g., 2024
    - month: 1-12
    
    Returns income, expense, and net balance for that month
    """
    summary = DashboardService.get_monthly_summary(db, current_user.user.id, year, month)
    return summary

@router.get(
    "/quick-stats",
    response_model=dict,
    summary="Get quick stats",
    responses={
        200: {"description": "Quick statistics"},
        401: {"description": "Not authenticated"}
    }
)
def get_quick_stats(
    current_user: CurrentUser = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get quick statistics - useful for dashboard widgets
    
    Returns key metrics in a compact format
    """
    return {
        "total_income": DashboardService.get_total_income(db, current_user.user.id),
        "total_expense": DashboardService.get_total_expense(db, current_user.user.id),
        "net_balance": DashboardService.get_balance(db, current_user.user.id),
        "user_role": current_user.user.role.value,
        "currency": "USD"
    }

@router.get(
    "/admin/stats",
    response_model=dict,
    summary="Get admin statistics",
    responses={
        200: {"description": "Admin statistics"},
        403: {"description": "Admin access required"},
        401: {"description": "Not authenticated"}
    }
)
def get_admin_stats(
    current_user: CurrentUser = Depends(require_analyst_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics (Analyst+ only)
    
    Returns statistics for analytical purposes
    """
    from sqlalchemy import func
    from models import FinancialRecord
    
    total_records = db.query(func.count(FinancialRecord.id)).scalar()
    total_users = db.query(func.count(FinancialRecord.user_id)).distinct().scalar()
    
    total_income = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == "income"
    ).scalar() or 0
    
    total_expense = db.query(func.sum(FinancialRecord.amount)).filter(
        FinancialRecord.type == "expense"
    ).scalar() or 0
    
    return {
        "total_records": total_records,
        "total_users_with_records": total_users,
        "system_income": total_income,
        "system_expense": total_expense,
        "net_flow": total_income - total_expense,
        "accessed_by": current_user.user.email
    }
