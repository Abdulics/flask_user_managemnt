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

        # Only admins can edit role
        if not getattr(actor, "role", None) == Role.ADMIN:
            try:
                del self.role
            except AttributeError:
                pass
        else:
            # Admin cannot demote self
            if target and actor.id == target.id:
                self.role.render_kw = {"disabled": True}

        # Non-admins cannot edit username/email of others
        if actor and target and actor.id != target.id:
            self.username.render_kw = {"readonly": True}
            self.email.render_kw = {"readonly": True}

        # You can also set read-only for other sensitive Employee fields if needed
        # e.g., salary only editable by Admin
        if not (actor.role == Role.ADMIN):
            self.salary.render_kw = {"readonly": True}

    def validate_role(self, field):
        if not hasattr(self, "role"):
            return

        if getattr(self.actor, "role", None) != Role.ADMIN:
            raise ValidationError("You do not have permission to change roles.")

        if self.target and self.actor.id == self.target.id and field.data != Role.ADMIN.name:
            raise ValidationError("You cannot remove your own ADMIN role.")

    def apply_changes(self, user, employee):
        """Apply form data to User and Employee objects."""
        user.username = self.username.data
        user.email = self.email.data
        user.bio = self.bio.data
        if hasattr(self, "role") and not (self.target and self.actor.id == self.target.id and getattr(self.role, "render_kw", {}).get("disabled")):
            user.role = Role[self.role.data]

        # Employee fields are mostly read-only, but you can allow Admins to update some
        # e.g., department, position, salary if desired
        if self.actor.role == Role.ADMIN:
            employee.department = self.department.data
            employee.position = self.position.data
            employee.salary = self.salary.data
