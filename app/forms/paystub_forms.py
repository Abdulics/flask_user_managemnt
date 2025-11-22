from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class PaystubForm(FlaskForm):
    employee_id = SelectField("Employee", coerce=int, validators=[DataRequired()])
    pay_period_start = DateField("Pay Period Start", validators=[DataRequired()])
    pay_period_end = DateField("Pay Period End", validators=[DataRequired()])
    gross_pay = DecimalField("Gross Pay", validators=[DataRequired(), NumberRange(min=0)])
    taxes = DecimalField("Taxes", validators=[DataRequired(), NumberRange(min=0)])
    deductions = DecimalField("Deductions", validators=[DataRequired(), NumberRange(min=0)])
    issued_at = DateField("Issued At", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Create")
