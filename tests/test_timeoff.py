from app.models.timeoff import TimeOff, TimeOffStatus
from app import db
from tests.conftest import login


def test_manager_sends_pending_timeoff_to_hr_queue(client, app):
    login(client, "manager")

    response = client.post("/timeoff/1/approve", data={"stage": "manager"}, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        request = db.session.get(TimeOff, 1)
        assert request.status == TimeOffStatus.MANAGER_APPROVED


def test_hr_employee_can_approve_hr_queue_item(client, app):
    login(client, "hr_user")

    response = client.post("/timeoff/2/approve", data={"stage": "hr"}, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        request = db.session.get(TimeOff, 2)
        assert request.status == TimeOffStatus.APPROVED


def test_non_hr_employee_cannot_view_hr_queue(client):
    login(client, "employee")

    response = client.get("/timeoff/hr", follow_redirects=True)

    assert b"Access denied. HR only." in response.data


def test_employee_can_cancel_own_pending_timeoff(client, app):
    login(client, "employee")

    response = client.post("/timeoff/1/cancel", follow_redirects=True)

    assert response.status_code == 200
    assert b"Time-off request cancelled." in response.data
    with app.app_context():
        request = db.session.get(TimeOff, 1)
        assert request.status == TimeOffStatus.CANCELLED
