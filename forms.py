from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    type = SelectField('Type', choices=[('expense', 'Expense'), ('income', 'Income')], validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired(), Length(max=7)])
    icon = StringField('Icon', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Save Category')


class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Expense')


class IncomeForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Income')


class BudgetForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    month = SelectField('Month', coerce=int, validators=[DataRequired()], 
                        choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), 
                                 (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
                                 (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])
    year = SelectField('Year', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Budget')


class DateRangeForm(FlaskForm):
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Filter')
