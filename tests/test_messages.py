from tests.conftest import login


def test_message_compose_lists_users_across_roles(client):
    login(client, "employee")

    response = client.get("/messages/compose")

    assert response.status_code == 200
    assert b"admin - admin" in response.data
    assert b"hr_user - employee" in response.data


def test_user_can_send_message_to_any_other_user(client):
    login(client, "employee")

    response = client.post(
        "/messages/compose",
        data={"recipient_id": "1", "subject": "Hello Admin", "body": "A test message"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Message sent successfully!" in response.data
