from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Login form for user authentication."""
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email address',
        'autocomplete': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your password',
        'autocomplete': 'current-password'
    })
    
    remember_me = BooleanField('Remember me', render_kw={
        'class': 'form-check-input'
    })
    
    submit = SubmitField('Sign In', render_kw={
        'class': 'btn btn-primary btn-lg w-100'
    })

class SignupForm(FlaskForm):
    """Signup form for user registration."""
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email must be less than 120 characters.')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter your email address',
        'autocomplete': 'email'
    })
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Create a password (min. 6 characters)',
        'autocomplete': 'new-password'
    })
    
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ], render_kw={
        'class': 'form-control form-control-lg',
        'placeholder': 'Confirm your password',
        'autocomplete': 'new-password'
    })
    
    submit = SubmitField('Create Account', render_kw={
        'class': 'btn btn-primary btn-lg w-100'
    })
    
    def validate_email(self, field):
        """Check if email is already registered."""
        user = User.get_by_email(field.data.lower().strip())
        if user:
            raise ValidationError('This email address is already registered. Please use a different email or sign in.')