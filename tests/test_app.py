import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

BASE_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activity state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_initial_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "alice@example.com"

    # Act
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert signup_response.status_code == 200
    assert f"Signed up {email} for {activity_name}" in signup_response.json()["message"]

    # Act
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert email in participants


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": participant_email}
    )

    # Assert
    assert delete_response.status_code == 200
    assert f"Removed {participant_email} from {activity_name}" in delete_response.json()["message"]

    # Act
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert participant_email not in participants
