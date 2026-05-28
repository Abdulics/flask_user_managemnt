from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, ValidationError
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

    def validate_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("End date must be on or after the start date.")
