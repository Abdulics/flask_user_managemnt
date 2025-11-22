from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.paystub import Paystub
from app.models.employees import Employee, Role
from app.utils.decorators import role_required
from app.forms.paystub_forms import PaystubForm

paystub_bp = Blueprint('paystubs', __name__, url_prefix='/paystubs')


@paystub_bp.route('/')
@login_required
def my_paystubs():
    """Employees view their own paystubs."""
    paystubs = Paystub.query.filter_by(employee_id=current_user.id).order_by(Paystub.pay_period_end.desc()).all()
    return render_template('paystubs/index.html', paystubs=paystubs)


@paystub_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN)
def create_paystub():
    """Admins can generate paystubs for any user."""
    form = PaystubForm()
    form.employee_id.choices = [
        (emp.user.id, f"{emp.full_name} ({emp.user.username})") for emp in Employee.query.all() if emp.user
    ]

    if form.validate_on_submit():
        paystub = Paystub(
            employee_id=form.employee_id.data,
            pay_period_start=form.pay_period_start.data,
            pay_period_end=form.pay_period_end.data,
            gross_pay=form.gross_pay.data,
            taxes=form.taxes.data,
            deductions=form.deductions.data,
            notes=form.notes.data or None,
            issued_at=form.issued_at.data,
        )
        paystub.calculate_net_pay()
        paystub.validate_dates()
        db.session.add(paystub)
        db.session.commit()
        flash('Paystub created.', 'success')
        return redirect(url_for('paystubs.my_paystubs'))

    return render_template('paystubs/create.html', form=form)
