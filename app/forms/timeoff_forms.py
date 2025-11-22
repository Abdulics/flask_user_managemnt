from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.models.timeoff import TimeOffType


class TimeOffRequestForm(FlaskForm):
    type = SelectField(
        "Type",
        choices=[(t.value, t.value.capitalize()) for t in TimeOffType],
        validators=[DataRequired()]
    )
    start_date = DateField("Start Date", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    reason = TextAreaField("Reason", validators=[Optional()])
    submit = SubmitField("Submit")
