from tests.conftest import login


def test_employee_sees_own_paystub(client):
    login(client, "employee")

    response = client.get("/paystubs/")

    assert response.status_code == 200
    assert b"1000.00" in response.data


def test_other_employee_does_not_see_someone_elses_paystub(client):
    login(client, "other")

    response = client.get("/paystubs/")

    assert response.status_code == 200
    assert b"1000.00" not in response.data
