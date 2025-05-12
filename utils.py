from sqlalchemy import func, extract
from datetime import datetime
from models import Expense, Income, Category, Budget

def get_month_name(month_number):
    """Return the name of the month from the month number."""
    return datetime(2000, month_number, 1).strftime('%B')

def get_chart_colors():
    """Return a list of colors for chart."""
    return [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#8AC249', '#EA80FC', '#00BCD4', '#FF5722'
    ]

def get_monthly_summary(user_id, month, year):
    """Get total income and expenses for a specific month and year."""
    from app import db
    
    # Calculate total income for the month
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        extract('month', Income.date) == month,
        extract('year', Income.date) == year
    ).scalar() or 0
    
    # Calculate total expenses for the month
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).scalar() or 0
    
    return {
        'income': total_income,
        'expenses': total_expenses,
        'savings': total_income - total_expenses
    }
