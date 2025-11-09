from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, FloatField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models import Role

class UserProfileForm(FlaskForm):
    """
    Combined User + Employee profile form with role-based access.

    Purpose:
    - Allow a user to view their complete profile, including associated Employee data.
    - Allow editing of fields according to the user's role.

    Behavior:
    - Pass `actor` (the user performing the change, e.g., current_user) to the constructor.
    - Pass `target` (the user being edited, or None for create).
    - Only the owner of the profile or an admin can edit username and email.
    - Only admins can see/edit the `role` field; other users cannot change roles.
    - Admins cannot demote themselves from the ADMIN role.
    - Employee-related fields (name, employee_id, department, position, salary, etc.) are view-only for non-admins.
    - Password handling is separate and not included in this form.
    - Apply changes to both `User` and `Employee` objects via `apply_changes()`.

    Usage:
        form = UserProfileForm(actor=current_user, target=user)
        if form.validate_on_submit():
            form.apply_changes(user, user.employee)
    """

    # User fields
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    bio = StringField("Bio", validators=[Optional(), Length(max=200)])
    is_active = BooleanField("Active")
    role = SelectField("Role", choices=[(r.name, r.value) for r in Role])

    # Employee fields (read-only for non-admin/manager)
    employee_id = StringField("Employee ID", render_kw={"readonly": True})
    first_name = StringField("First Name", render_kw={"readonly": True})
    last_name = StringField("Last Name", render_kw={"readonly": True})
    department = StringField("Department", render_kw={"readonly": True})
    position = StringField("Position", render_kw={"readonly": True})
    hire_date = DateField("Hire Date", render_kw={"readonly": True})
    salary = FloatField("Salary", render_kw={"readonly": True})
    manager_id = StringField("Manager ID", render_kw={"readonly": True})

    submit = SubmitField("Save")

    def __init__(self, actor=None, target=None, *args, **kwargs):
        """
        actor: current_user performing the edit
        target: user being edited
        """
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.target = target

        # Admin cannot change own role
        if actor and target and actor.role == Role.ADMIN:
            if actor.id == target.id:
                self.role.render_kw = {"disabled": True}  # Keep field visible but not editable
            else:
                self.role.render_kw = {}  # Editable

        # Non-admins cannot edit role
        elif actor and getattr(actor, "role", None) != Role.ADMIN:
            try:
                del self.role
            except AttributeError:
                pass

        # Non-admins cannot edit username/email of others
        if actor and target and actor.id != target.id and actor.role != Role.ADMIN:
            self.username.render_kw = {"readonly": True}
            self.email.render_kw = {"readonly": True}

        # Employee fields
        if actor.role != Role.ADMIN:
            for field_name in [
                "employee_id", "first_name", "last_name", 
                "department", "position", "hire_date", "salary", "manager_id", "is_active"
            ]:
                getattr(self, field_name).render_kw = {"readonly": True}


    def validate_role(self, field):
        if not hasattr(self, "role"):
            return

        if getattr(self.actor, "role", None) != Role.ADMIN:
            raise ValidationError("You do not have permission to change roles.")

        if self.target and self.actor.id == self.target.id and field.data != Role.ADMIN.name:
            raise ValidationError("You cannot remove your own ADMIN role.")

    def apply_changes(self, target_user):
        """Apply form data to User and Employee objects."""
        # Basic user fields
        target_user.username = self.username.data
        target_user.email = self.email.data
        target_user.bio = self.bio.data

        # Role field: only admin editing others can change
        if hasattr(self, "role") and self.actor.role == Role.ADMIN and self.actor.id != target_user.id:
            target_user.role = Role[self.role.data]

        # Employee fields: only admin can edit, including their own employee record
        if self.actor.role == Role.ADMIN and getattr(target_user, "employee", None):
            target_user.employee.employee_id = self.employee_id.data
            target_user.employee.first_name = self.first_name.data
            target_user.employee.last_name = self.last_name.data
            target_user.employee.department = self.department.data
            target_user.employee.position = self.position.data
            target_user.employee.hire_date = self.hire_date.data
            target_user.employee.salary = self.salary.data
            target_user.employee.manager_id = self.manager_id.data

