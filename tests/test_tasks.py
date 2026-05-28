from app.models.task import Task
from tests.conftest import login


def test_employee_cannot_open_create_task(client):
    login(client, "employee")

    response = client.get("/tasks/create", follow_redirects=True)

    assert response.status_code == 200
    assert b"Access denied" in response.data


def test_manager_can_assign_task_to_own_subordinate(client, app):
    login(client, "manager")

    response = client.post(
        "/tasks/create",
        data={
            "title": "Manager Assigned",
            "description": "Allowed",
            "assigned_to_id": "3",
            "priority": "high",
            "due_date": "2030-01-01",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with app.app_context():
        assert Task.query.filter_by(title="Manager Assigned").first() is not None


def test_manager_cannot_assign_task_outside_team(client, app):
    login(client, "manager")

    response = client.post(
        "/tasks/create",
        data={
            "title": "Outside Team",
            "description": "Blocked",
            "assigned_to_id": "4",
            "priority": "medium",
            "due_date": "2030-01-01",
        },
        follow_redirects=True,
    )

    assert b"Managers can only assign tasks to their own team members." in response.data
    with app.app_context():
        assert Task.query.filter_by(title="Outside Team").first() is None
