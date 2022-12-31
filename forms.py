from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=55)])
    
    email = StringField("Email", validators=[InputRequired(message="required"), Length(max=50), Email()])
    
    first_name = StringField("First Name", validators=[InputRequired(message="required"), Length(max=50)])
    
    last_name = StringField("Last Name", validators=[InputRequired(message="required"), Length(max=50)])
    
    


class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(message="required")])
    
    password = PasswordField("Password", validators=[InputRequired(message="required")])


class FeedbackForm(FlaskForm):
    """Form for submitting or editing feedback."""
    
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = StringField("Content", validators=[InputRequired()])
    
    