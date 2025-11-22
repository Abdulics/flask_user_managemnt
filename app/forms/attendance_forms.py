from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from app.models.attendance import AttendanceStatus


class AttendanceForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[(s.value, s.name.title()) for s in AttendanceStatus],
        validators=[DataRequired()]
    )
    note = StringField("Note", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Save")
