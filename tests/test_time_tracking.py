from app.models.time_entry import TimeEntry
from tests.conftest import login


def test_clock_in_creates_active_entry(client, app):
    login(client, "other")

    response = client.post("/time-tracker/clock-in", follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        active = TimeEntry.query.filter_by(user_id=4, clock_out=None).count()
        assert active == 1


def test_duplicate_clock_in_is_blocked(client, app):
    login(client, "other")

    client.post("/time-tracker/clock-in", follow_redirects=True)
    response = client.post("/time-tracker/clock-in", follow_redirects=True)

    assert b"Already clocked in." in response.data
    with app.app_context():
        active = TimeEntry.query.filter_by(user_id=4, clock_out=None).count()
        assert active == 1
