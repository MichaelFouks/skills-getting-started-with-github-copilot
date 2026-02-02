import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def _reset_between_tests():
    reset_activities()
    yield
    reset_activities()


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]


def test_signup_success():
    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    activities_response = client.get("/activities")
    participants = activities_response.json()["Basketball Team"]["participants"]
    assert "newstudent@mergington.edu" in participants


def test_signup_duplicate():
    response = client.post(
        "/activities/Basketball%20Team/signup",
        params={"email": "alex@mergington.edu"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    response = client.delete(
        "/activities/Drama%20Club/participants",
        params={"email": "james@mergington.edu"},
    )
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]

    activities_response = client.get("/activities")
    participants = activities_response.json()["Drama Club"]["participants"]
    assert "james@mergington.edu" not in participants


def test_unregister_missing_participant():
    response = client.delete(
        "/activities/Drama%20Club/participants",
        params={"email": "unknown@mergington.edu"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
