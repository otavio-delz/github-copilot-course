"""
Tests for the Mergington High School API

This module contains comprehensive tests for all API endpoints including:
- Root endpoint
- Activities listing
- Activity signup
- Activity unregistration
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
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
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and participate in competitions",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums including painting and sculpture",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "ethan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["noah@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through debates",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["alexander@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Clear and restore activities
    activities.clear()
    activities.update(original_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to the static index page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Soccer Team" in data
        assert "Swimming Club" in data
        assert "Art Club" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Olympiad" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has the correct data structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_participants(self, client):
        """Test that activities include their current participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test successful signup for an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up newstudent@mergington.edu for Chess Club"
        }

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify the participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email(self, client):
        """Test that signing up twice with the same email returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]

    def test_signup_with_spaces_in_activity_name(self, client):
        """Test signup works correctly with activity names containing spaces"""
        response = client.post(
            "/activities/Science Olympiad/signup?email=scientist@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_existing_activity(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from Chess Club"
        }

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant from the activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify the participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_signed_up(self, client):
        """Test that unregistering when not signed up returns 400"""
        email = "notsignedup@mergington.edu"
        response = client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"

    def test_signup_and_unregister_flow(self, client):
        """Test complete flow of signing up and then unregistering"""
        email = "flowtest@mergington.edu"
        
        # Sign up
        signup_response = client.post(f"/activities/Drama Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Drama Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/Drama Club/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Drama Club"]["participants"]

    def test_unregister_with_spaces_in_activity_name(self, client):
        """Test unregister works correctly with activity names containing spaces"""
        email = "alexander@mergington.edu"  # Already in Science Olympiad
        response = client.delete(f"/activities/Science Olympiad/unregister?email={email}")
        assert response.status_code == 200


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_activity_names_are_case_sensitive(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_multiple_participants_in_activity(self, client):
        """Test that multiple participants can be in the same activity"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club already has 2 participants
        assert len(data["Chess Club"]["participants"]) >= 2

    def test_empty_email_parameter(self, client):
        """Test behavior with empty email parameter"""
        response = client.post("/activities/Chess Club/signup?email=")
        # FastAPI will accept empty string, but our app should handle it
        # The behavior depends on business requirements
        assert response.status_code in [200, 400, 422]
