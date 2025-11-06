from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

class UserForm(FlaskForm):
    """
    Generic user create/edit form.

    Behavior:
    - Pass actor (the user performing the change, e.g. current_user) to the constructor.
    - Pass target (the user being edited, or None for create).
    - Only an actor with is_admin == True may see/change the is_admin checkbox.
    - An admin actor may not remove their own admin flag.
    - Password is optional for edit; if left blank no password change is applied.
    """

    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[Optional(), EqualTo("password")])
    bio = StringField("Bio", validators=[Optional(), Length(max=200)])
    is_active = BooleanField("Active", default=True)
    is_admin = BooleanField("Admin", default=False)
    
    submit = SubmitField("Save")

    def __init__(self, actor=None, target=None, *args, **kwargs):
        """
        actor: the user performing the change (object with at least `is_admin` and `id` attributes)
        target: the user being edited (object with at least `is_admin` and `id`), or None
        """
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.target = target

        # If the actor is not an admin, remove the is_admin field entirely so it won't be rendered or validated.
        if not getattr(self.actor, "is_admin", False):
            # deleting the attribute prevents rendering and validation for non-admin actors.
            try:
                del self.is_admin
            except Exception:
                pass
        else:
            # If an admin is editing their own account, disable changing their admin flag.
            if self.target is not None and getattr(self.actor, "id", None) == getattr(self.target, "id", None):
                # mark the field as disabled for HTML rendering; the validator will also block demotion.
                self.is_admin.render_kw = {"disabled": True}
        

    def validate_is_admin(self, field):
        # This validator only runs when is_admin is present (i.e., actor is admin).
        if not getattr(self.actor, "is_admin", False):
            raise ValidationError("You do not have permission to change admin status.")

        # Prevent an admin from removing their own admin flag.
        if self.target is not None and getattr(self.actor, "id", None) == getattr(self.target, "id", None):
            # If the target currently is admin but submitted unchecked, block it.
            if getattr(self.target, "is_admin", False) and not field.data:
                raise ValidationError("You cannot remove your own admin privileges.")

    def apply_changes(self, user):
        """
        Apply validated form data to a user object.
        The user object is expected to have attributes: username, email, is_active, is_admin and either
        a set_password(password) method or a password attribute.
        """
        user.username = self.username.data
        user.email = self.email.data
        user.is_active = bool(self.is_active.data)
        user.bio = self.bio.data

        # Only update is_admin if the field exists on this form (actor was admin).
        if hasattr(self, "is_admin"):
            # If the admin field was disabled for self-edit, skip changing it.
            if not (
                self.target is not None
                and getattr(self.actor, "id", None) == getattr(self.target, "id", None)
                and getattr(self.is_admin, "render_kw", {}).get("disabled")
            ):
                user.is_admin = bool(self.is_admin.data)
                
        # Update password only if provided
        if self.password.data.strip():
            if hasattr(user, "set_password") and callable(user.set_password):
                user.set_password(self.password.data)
            else:
                user.password = self.password.data
