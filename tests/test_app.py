def test_root_redirects_to_frontend(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity in activities
    assert set(activities[expected_activity]) == {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }
    assert isinstance(activities[expected_activity]["participants"], list)


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_supports_url_encoded_activity_names(client):
    # Arrange
    activity_name = "Chess Club"
    email = "encoded.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_delete_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_delete_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_rejects_unregistered_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_delete_requires_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_activity_state_is_reset_between_tests(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "isolated.student@mergington.edu"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert email not in response.json()[activity_name]["participants"]
