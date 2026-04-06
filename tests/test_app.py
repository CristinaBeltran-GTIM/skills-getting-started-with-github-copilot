import copy
import pytest
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_data = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_data))


def test_root_redirects_to_static_index():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    client = TestClient(app)
    signup_url = "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_unregisters_participant():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    delete_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_missing_participant_returns_400():
    # Arrange
    client = TestClient(app)
    email = "missing@student.edu"
    activity_name = "Chess Club"
    delete_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"
