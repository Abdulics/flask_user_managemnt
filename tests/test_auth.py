from app.models.user import User
from tests.conftest import login


def test_login_with_valid_credentials_reaches_dashboard(client):
    response = login(client, "employee")

    assert response.status_code == 200
    assert b"Welcome back, employee!" in response.data


def test_login_rejects_unsafe_next_redirect(client):
    response = client.post(
        "/auth/login?next=https://evil.example/",
        data={"username": "employee", "password": "password123"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_change_password_updates_hash(client, app):
    login(client, "employee")

    response = client.post(
        "/auth/change-password",
        data={
            "current_password": "password123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Password changed successfully." in response.data
    with app.app_context():
        user = User.query.filter_by(username="employee").first()
        assert user.check_password("newpass123")
