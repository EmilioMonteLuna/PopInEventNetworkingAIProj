import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_user_and_get_user():
    user_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "job_title": "Engineer",
        "company": "TestCorp",
        "industry": "Tech",
        "bio": "Test bio",
        "experience_years": 3,
        "linkedin_url": "https://linkedin.com/in/testuser",
        "interests": ["AI", "Networking"],
        "goals": ["Meet founders", "Find cofounder"]
    }
    create_resp = client.post("/users", json=user_data)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]
    get_resp = client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == user_data["email"]

def test_create_event_and_register_user():
    event_data = {
        "name": "Test Event",
        "description": "A test event.",
        "date": "2025-08-01T10:00:00",
        "location": "Toronto",
        "venue": "Test Venue",
        "city": "Toronto",
        "country": "Canada",
        "max_attendees": 100,
        "event_type": "Conference"
    }
    event_resp = client.post("/events", json=event_data)
    assert event_resp.status_code == 201
    event_id = event_resp.json()["id"]
    # Create a user
    user_data = {
        "name": "Event User",
        "email": "eventuser@example.com",
        "job_title": "Manager",
        "company": "EventCorp",
        "industry": "Events",
        "bio": "Event bio",
        "experience_years": 5,
        "linkedin_url": "https://linkedin.com/in/eventuser",
        "interests": ["Events"],
        "goals": ["Network"]
    }
    user_resp = client.post("/users", json=user_data)
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]
    reg_resp = client.post(f"/events/{event_id}/register/{user_id}")
    assert reg_resp.status_code == 200
    assert "successfully registered" in reg_resp.json()["message"]

def test_visualization_cluster_map_empty():
    # Should return 404 for non-existent event
    resp = client.get("/visualization/cluster-map?event_id=99999")
    assert resp.status_code == 404
    assert "error" in resp.json()

