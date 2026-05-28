from app.models.team import Team
from tests.conftest import login


def test_employee_cannot_create_team(client):
    login(client, "employee")

    response = client.get("/admin/teams/create", follow_redirects=True)

    assert b"Access denied. Team management is for admins, managers, and HR." in response.data


def test_admin_can_edit_team(client, app):
    login(client, "admin", "admin123")

    response = client.post(
        "/admin/teams/1/edit",
        data={"name": "Updated Operations", "description": "Updated", "department_id": "1", "lead_id": "1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        team = Team.query.filter_by(name="Updated Operations").first()
        assert team is not None
