from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

class DashboardActionForm(FlaskForm):
    action = SelectField('Choose Action', choices=[
        ('view_profile', 'View Profile'),
        ('update_settings', 'Update Settings'),
        ('logout', 'Logout')
    ], validators=[DataRequired()])
    submit = SubmitField('Go')