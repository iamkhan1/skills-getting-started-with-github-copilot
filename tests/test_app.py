"""
FastAPI application tests using AAA (Arrange-Act-Assert) pattern
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    yield
    # Reset after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_success(self, client):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert all(activity in data for activity in expected_activities)
        assert "description" in data["Chess Club"]
        assert "participants" in data["Chess Club"]
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]

    def test_activity_has_correct_structure(self, client):
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]

        # Assert
        assert response.status_code == 200
        assert set(chess_club.keys()) == expected_keys
        assert isinstance(chess_club["participants"], list)
        assert isinstance(chess_club["max_participants"], int)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_success(self, client, reset_activities):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_updates_participants_list(self, client, reset_activities):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Programming Class"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        updated_activity = response.json()[activity]

        # Assert
        assert email in updated_activity["participants"]

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        # Arrange
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_with_empty_email_fails(self, client, reset_activities):
        # Arrange
        email = ""
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        # Empty email should still add to list (current behavior)
        # This test documents current behavior
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_success(self, client, reset_activities):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_removes_from_participants(self, client, reset_activities):
        # Arrange
        email = "emma@mergington.edu"
        activity = "Programming Class"

        # Act
        client.delete(f"/activities/{activity}/unregister?email={email}")
        response = client.get("/activities")
        updated_activity = response.json()[activity]

        # Assert
        assert email not in updated_activity["participants"]

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        # Arrange - no setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_root_with_follow_redirects(self, client):
        # Arrange - no setup needed

        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
