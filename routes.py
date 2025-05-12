import csv
import io
from datetime import datetime, timedelta, date
from calendar import monthrange
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import extract, func
from app import app, db
from models import User, Category, Expense, Income, Budget
from forms import (LoginForm, RegistrationForm, CategoryForm, ExpenseForm, 
                  IncomeForm, BudgetForm, DateRangeForm)
from utils import get_month_name, get_chart_colors, get_monthly_summary


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create default categories for new user
        default_expense_categories = [
            {'name': 'Food', 'color': '#FF5733', 'icon': 'fa-utensils'},
            {'name': 'Housing', 'color': '#33A8FF', 'icon': 'fa-home'},
            {'name': 'Transportation', 'color': '#33FF57', 'icon': 'fa-car'},
            {'name': 'Utilities', 'color': '#F033FF', 'icon': 'fa-bolt'},
            {'name': 'Entertainment', 'color': '#FF3369', 'icon': 'fa-film'},
            {'name': 'Healthcare', 'color': '#33FFF0', 'icon': 'fa-medkit'},
            {'name': 'Clothing', 'color': '#7D33FF', 'icon': 'fa-tshirt'},
            {'name': 'Other', 'color': '#808080', 'icon': 'fa-ellipsis-h'}
        ]
        
        default_income_categories = [
            {'name': 'Salary', 'color': '#4CAF50', 'icon': 'fa-money-bill'},
            {'name': 'Freelance', 'color': '#2196F3', 'icon': 'fa-laptop'},
            {'name': 'Investments', 'color': '#FFC107', 'icon': 'fa-chart-line'},
            {'name': 'Gifts', 'color': '#E91E63', 'icon': 'fa-gift'},
            {'name': 'Other Income', 'color': '#9C27B0', 'icon': 'fa-plus-circle'}
        ]
        
        for cat in default_expense_categories:
            category = Category(
                name=cat['name'],
                type='expense',
                color=cat['color'],
                icon=cat['icon'],
                user_id=user.id
            )
            db.session.add(category)
        
        for cat in default_income_categories:
            category = Category(
                name=cat['name'],
                type='income',
                color=cat['color'],
                icon=cat['icon'],
                user_id=user.id
            )
            db.session.add(category)
        
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month and year
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get start and end date of current month
    start_date = date(current_year, current_month, 1)
    _, last_day = monthrange(current_year, current_month)
    end_date = date(current_year, current_month, last_day)
    
    # Get summary data for current month
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).scalar() or 0
    
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).scalar() or 0
    
    net_savings = total_income - total_expenses
    
    # Get recent transactions
    recent_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).limit(5).all()
    recent_incomes = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).limit(5).all()
    
    # Get all categories for the pie chart
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()
    income_categories = Category.query.filter_by(user_id=current_user.id, type='income').all()
    
    # Get budget vs actual
    budgets = Budget.query.filter_by(
        user_id=current_user.id, 
        month=current_month,
        year=current_year
    ).all()
    
    # Calculate budget status
    budget_data = []
    total_budget = 0
    
    for budget in budgets:
        category_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).scalar() or 0
        
        percentage = min(int((category_expenses / budget.amount) * 100) if budget.amount > 0 else 0, 100)
        
        budget_data.append({
            'category': budget.category.name,
            'budget': budget.amount,
            'spent': category_expenses,
            'percentage': percentage,
            'color': budget.category.color
        })
        
        total_budget += budget.amount
    
    # Get monthly summary for the last 6 months
    months_data = []
    for i in range(5, -1, -1):
        month_date = current_date - timedelta(days=30 * i)
        month_num = month_date.month
        year_num = month_date.year
        month_summary = get_monthly_summary(current_user.id, month_num, year_num)
        months_data.append({
            'month': get_month_name(month_num),
            'income': month_summary['income'],
            'expenses': month_summary['expenses']
        })
    
    return render_template(
        'dashboard.html', 
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=net_savings,
        recent_expenses=recent_expenses,
        recent_incomes=recent_incomes,
        expense_categories=expense_categories,
        income_categories=income_categories,
        budget_data=budget_data,
        total_budget=total_budget,
        months_data=months_data,
        current_month=get_month_name(current_month),
        current_year=current_year
    )


@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    # Populate category dropdown
    form.category_id.choices = [(c.id, c.name) for c in 
                               Category.query.filter_by(user_id=current_user.id, type='expense').all()]
    
    if form.validate_on_submit():
        expense = Expense(
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    # Default to current date
    if request.method == 'GET':
        form.date.data = datetime.today()
    
    # Get all expenses
    expenses_list = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    return render_template('expenses.html', form=form, expenses=expenses_list)


@app.route('/expense/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('You are not authorized to delete this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))


@app.route('/expense/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if expense.user_id != current_user.id:
        flash('You are not authorized to edit this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    form = ExpenseForm()
    form.category_id.choices = [(c.id, c.name) for c in 
                               Category.query.filter_by(user_id=current_user.id, type='expense').all()]
    
    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.description = form.description.data
        expense.date = form.date.data
        expense.category_id = form.category_id.data
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses'))
    
    # Populate form with existing data
    if request.method == 'GET':
        form.amount.data = expense.amount
        form.description.data = expense.description
        form.date.data = expense.date
        form.category_id.data = expense.category_id
    
    return render_template('expenses.html', form=form, editing=True, expense_id=expense_id, expenses=Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all())


@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    form = IncomeForm()
    # Populate category dropdown
    form.category_id.choices = [(c.id, c.name) for c in 
                               Category.query.filter_by(user_id=current_user.id, type='income').all()]
    
    if form.validate_on_submit():
        income = Income(
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(income)
        db.session.commit()
        flash('Income added successfully!', 'success')
        return redirect(url_for('income'))
    
    # Default to current date
    if request.method == 'GET':
        form.date.data = datetime.today()
    
    # Get all income
    income_list = Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all()
    
    return render_template('income.html', form=form, incomes=income_list)


@app.route('/income/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.user_id != current_user.id:
        flash('You are not authorized to delete this income.', 'danger')
        return redirect(url_for('income'))
    
    db.session.delete(income)
    db.session.commit()
    flash('Income deleted successfully!', 'success')
    return redirect(url_for('income'))


@app.route('/income/edit/<int:income_id>', methods=['GET', 'POST'])
@login_required
def edit_income(income_id):
    income = Income.query.get_or_404(income_id)
    if income.user_id != current_user.id:
        flash('You are not authorized to edit this income.', 'danger')
        return redirect(url_for('income'))
    
    form = IncomeForm()
    form.category_id.choices = [(c.id, c.name) for c in 
                               Category.query.filter_by(user_id=current_user.id, type='income').all()]
    
    if form.validate_on_submit():
        income.amount = form.amount.data
        income.description = form.description.data
        income.date = form.date.data
        income.category_id = form.category_id.data
        
        db.session.commit()
        flash('Income updated successfully!', 'success')
        return redirect(url_for('income'))
    
    # Populate form with existing data
    if request.method == 'GET':
        form.amount.data = income.amount
        form.description.data = income.description
        form.date.data = income.date
        form.category_id.data = income.category_id
    
    return render_template('income.html', form=form, editing=True, income_id=income_id, incomes=Income.query.filter_by(user_id=current_user.id).order_by(Income.date.desc()).all())


@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    form = BudgetForm()
    # Populate category dropdown
    form.category_id.choices = [(c.id, c.name) for c in 
                               Category.query.filter_by(user_id=current_user.id, type='expense').all()]
    
    # Populate year dropdown (current year and next year)
    current_year = datetime.now().year
    form.year.choices = [(current_year, str(current_year)), (current_year + 1, str(current_year + 1))]
    
    if form.validate_on_submit():
        # Check if budget already exists for this category, month, and year
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=form.category_id.data,
            month=form.month.data,
            year=form.year.data
        ).first()
        
        if existing_budget:
            existing_budget.amount = form.amount.data
            flash('Budget updated successfully!', 'success')
        else:
            budget = Budget(
                amount=form.amount.data,
                month=form.month.data,
                year=form.year.data,
                category_id=form.category_id.data,
                user_id=current_user.id
            )
            db.session.add(budget)
            flash('Budget added successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('budgets'))
    
    # Default to current month and year
    if request.method == 'GET':
        form.month.data = datetime.now().month
        form.year.data = current_year
    
    # Get all budgets for the current month and year
    current_month = datetime.now().month
    budgets_list = Budget.query.filter_by(
        user_id=current_user.id,
        month=current_month,
        year=current_year
    ).all()
    
    # Calculate current spending for each budget
    budget_data = []
    
    for budget in budgets_list:
        # Get start and end date of the month
        start_date = date(budget.year, budget.month, 1)
        _, last_day = monthrange(budget.year, budget.month)
        end_date = date(budget.year, budget.month, last_day)
        
        # Calculate total expenses for this category in this month
        category_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).scalar() or 0
        
        percentage = min(int((category_expenses / budget.amount) * 100) if budget.amount > 0 else 0, 100)
        
        budget_data.append({
            'id': budget.id,
            'category': budget.category.name,
            'amount': budget.amount,
            'spent': category_expenses,
            'remaining': budget.amount - category_expenses,
            'percentage': percentage,
            'color': budget.category.color
        })
    
    return render_template('budgets.html', form=form, budgets=budget_data, 
                          current_month=get_month_name(current_month), current_year=current_year)


@app.route('/budget/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    if budget.user_id != current_user.id:
        flash('You are not authorized to delete this budget.', 'danger')
        return redirect(url_for('budgets'))
    
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets'))


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            type=form.type.data,
            color=form.color.data,
            icon=form.icon.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('categories'))
    
    # Get all categories
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()
    income_categories = Category.query.filter_by(user_id=current_user.id, type='income').all()
    
    return render_template('categories.html', form=form, expense_categories=expense_categories, 
                          income_categories=income_categories)


@app.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('You are not authorized to delete this category.', 'danger')
        return redirect(url_for('categories'))
    
    # Check if category is being used in expenses or incomes
    if (len(category.expenses) > 0) or (len(category.incomes) > 0):
        flash('Cannot delete category as it is being used in transactions.', 'danger')
        return redirect(url_for('categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('categories'))


@app.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.user_id != current_user.id:
        flash('You are not authorized to edit this category.', 'danger')
        return redirect(url_for('categories'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.type = form.type.data
        category.color = form.color.data
        category.icon = form.icon.data
        
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories'))
    
    # Populate form with existing data
    if request.method == 'GET':
        form.name.data = category.name
        form.type.data = category.type
        form.color.data = category.color
        form.icon.data = category.icon
    
    # Get all categories
    expense_categories = Category.query.filter_by(user_id=current_user.id, type='expense').all()
    income_categories = Category.query.filter_by(user_id=current_user.id, type='income').all()
    
    return render_template('categories.html', form=form, editing=True, category_id=category_id,
                          expense_categories=expense_categories, income_categories=income_categories)


@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    form = DateRangeForm()
    
    # Default to current month
    today = datetime.today()
    if request.method == 'GET':
        form.start_date.data = date(today.year, today.month, 1)
        form.end_date.data = today.date()
    
    start_date = form.start_date.data or date(today.year, today.month, 1)
    end_date = form.end_date.data or today.date()
    
    # Get expenses by category within date range
    expenses_by_category = db.session.query(
        Category.name, Category.color, func.sum(Expense.amount)
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).group_by(Category.id).all()
    
    # Get income by category within date range
    income_by_category = db.session.query(
        Category.name, Category.color, func.sum(Income.amount)
    ).join(Income).filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).group_by(Category.id).all()
    
    # Calculate totals
    total_income = sum(amount for _, _, amount in income_by_category)
    total_expenses = sum(amount for _, _, amount in expenses_by_category)
    net_savings = total_income - total_expenses
    
    # Get daily expenses and income for line chart
    days = (end_date - start_date).days + 1
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    daily_expenses = []
    daily_income = []
    
    for day in date_range:
        # Get expenses for this day
        day_expenses = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.date == day
        ).scalar() or 0
        
        # Get income for this day
        day_income = db.session.query(func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            Income.date == day
        ).scalar() or 0
        
        daily_expenses.append({'date': day.strftime('%Y-%m-%d'), 'amount': day_expenses})
        daily_income.append({'date': day.strftime('%Y-%m-%d'), 'amount': day_income})
    
    # Get all transactions for the table
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).order_by(Expense.date.desc()).all()
    
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).order_by(Income.date.desc()).all()
    
    # Combine and sort transactions
    transactions = []
    for expense in expenses:
        transactions.append({
            'date': expense.date,
            'type': 'Expense',
            'category': expense.category.name,
            'description': expense.description,
            'amount': expense.amount,
            'color': expense.category.color
        })
    
    for income in incomes:
        transactions.append({
            'date': income.date,
            'type': 'Income',
            'category': income.category.name,
            'description': income.description,
            'amount': income.amount,
            'color': income.category.color
        })
    
    # Sort by date (newest first)
    transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('reports.html', form=form,
                          expenses_by_category=expenses_by_category,
                          income_by_category=income_by_category,
                          total_income=total_income,
                          total_expenses=total_expenses,
                          net_savings=net_savings,
                          daily_expenses=daily_expenses,
                          daily_income=daily_income,
                          transactions=transactions,
                          start_date=start_date,
                          end_date=end_date)


@app.route('/export/expenses', methods=['GET'])
@login_required
def export_expenses():
    # Get date range from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    except:
        start_date = None
        end_date = None
    
    # Default to current month if no dates provided
    if not start_date or not end_date:
        today = datetime.today()
        start_date = date(today.year, today.month, 1)
        end_date = today.date()
    
    # Query expenses within date range
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= start_date,
        Expense.date <= end_date
    ).order_by(Expense.date.desc()).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Category', 'Description', 'Amount'])
    
    # Write expenses
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category.name,
            expense.description,
            expense.amount
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'expenses_{start_date}_to_{end_date}.csv'
    )


@app.route('/export/income', methods=['GET'])
@login_required
def export_income():
    # Get date range from query parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    except:
        start_date = None
        end_date = None
    
    # Default to current month if no dates provided
    if not start_date or not end_date:
        today = datetime.today()
        start_date = date(today.year, today.month, 1)
        end_date = today.date()
    
    # Query income within date range
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).order_by(Income.date.desc()).all()
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Category', 'Description', 'Amount'])
    
    # Write incomes
    for income in incomes:
        writer.writerow([
            income.date.strftime('%Y-%m-%d'),
            income.category.name,
            income.description,
            income.amount
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'income_{start_date}_to_{end_date}.csv'
    )


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    # Count total transactions
    expenses_count = Expense.query.filter_by(user_id=current_user.id).count()
    incomes_count = Income.query.filter_by(user_id=current_user.id).count()
    
    # Get join date
    join_date = current_user.created_at.strftime('%B %d, %Y')
    
    # Calculate total lifetime income and expenses
    total_income = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id
    ).scalar() or 0
    
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id
    ).scalar() or 0
    
    # Calculate average monthly spending (last 3 months)
    today = datetime.today()
    three_months_ago = today - timedelta(days=90)
    
    recent_expenses = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.date >= three_months_ago.date()
    ).scalar() or 0
    
    avg_monthly_spending = recent_expenses / 3
    
    return render_template('profile.html', 
                          expenses_count=expenses_count,
                          incomes_count=incomes_count,
                          join_date=join_date,
                          total_income=total_income,
                          total_expenses=total_expenses,
                          avg_monthly_spending=avg_monthly_spending)


@app.route('/api/chart-data', methods=['GET'])
@login_required
def chart_data():
    chart_type = request.args.get('type', 'expense')
    month = int(request.args.get('month', datetime.now().month))
    year = int(request.args.get('year', datetime.now().year))
    
    # Get start and end date of the month
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    data = []
    
    if chart_type == 'expense':
        # Get expenses by category within date range
        expenses_by_category = db.session.query(
            Category.name, Category.color, func.sum(Expense.amount)
        ).join(Expense).filter(
            Expense.user_id == current_user.id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).group_by(Category.id).all()
        
        for name, color, amount in expenses_by_category:
            data.append({
                'label': name,
                'value': amount,
                'color': color
            })
    else:
        # Get income by category within date range
        income_by_category = db.session.query(
            Category.name, Category.color, func.sum(Income.amount)
        ).join(Income).filter(
            Income.user_id == current_user.id,
            Income.date >= start_date,
            Income.date <= end_date
        ).group_by(Category.id).all()
        
        for name, color, amount in income_by_category:
            data.append({
                'label': name,
                'value': amount,
                'color': color
            })
    
    return jsonify(data)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
