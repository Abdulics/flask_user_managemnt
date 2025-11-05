from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    """
    Form for user registration.
    Fields:
      - username
      - email
      - password
      - confirm_password
      - submit
    Validation:
      - username: required, 3-25 chars
      - email: required, valid email
      - password: required, min 6 chars
      - confirm_password: must match password
    """
    username = StringField(
        "Username",
        validators=[DataRequired(message="Username is required"), Length(min=3, max=25)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Email is required"), Email(message="Invalid email address")]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required"), Length(min=6)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """
    Form for user login.
    Fields:
      - username_or_email
      - password
      - remember (optional)
      - submit
    """
    username_or_email = StringField(
        "Username or Email",
        validators=[DataRequired(message="Username or email is required")]
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required")]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")