import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Test club",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["existing@example.com"],
        },
        "Art Club": {
            "description": "Another test club",
            "schedule": "Mondays",
            "max_participants": 3,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Art Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert activities["Art Club"]["participants"] == [email]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    email = "existing@example.com"
    initial_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities["Chess Club"]["participants"] == initial_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activities["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "existing@example.com"

    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unregistered_participant(client, activities):
    # Arrange
    email = "not-registered@example.com"
    initial_participants = activities["Chess Club"]["participants"].copy()

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert activities["Chess Club"]["participants"] == initial_participants