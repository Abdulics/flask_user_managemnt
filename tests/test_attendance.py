from tests.conftest import login


def test_regular_employee_cannot_view_team_attendance(client):
    login(client, "employee")

    response = client.get("/attendance/team", follow_redirects=True)

    assert b"Access denied. Team attendance is for managers, HR, and admins." in response.data


def test_hr_employee_can_view_team_attendance(client):
    login(client, "hr_user")

    response = client.get("/attendance/team")

    assert response.status_code == 200
    assert b"Team Attendance" in response.data or b"No attendance records found." in response.data
