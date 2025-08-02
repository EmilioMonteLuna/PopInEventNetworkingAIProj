"""
Comprehensive Test Suite for Event Networking AI System
End-to-end testing of the complete system functionality
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
import json

from main import app
from database.connection import get_db
from models.database import Base
from database.sample_data import create_sample_data

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)


class TestEventNetworkingSystem:
    """Complete system test suite"""

    def test_system_health(self):
        """Test system health endpoints"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Event Networking AI System" in response.json()["message"]

        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_user_creation_and_retrieval(self):
        """Test user management functionality"""
        # Create a user
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "job_title": "Software Engineer",
            "company": "Test Company",
            "industry": "Technology",
            "bio": "Test bio for networking",
            "experience_years": 5,
            "interests": ["Python", "Machine Learning", "AI"],
            "goals": ["Learn new skills", "Network with peers"]
        }

        response = client.post("/api/v1/users", json=user_data)
        assert response.status_code == 201

        created_user = response.json()
        assert created_user["name"] == "Test User"
        assert created_user["email"] == "test@example.com"
        assert len(created_user["interests"]) == 3
        assert len(created_user["goals"]) == 2

        # Retrieve the user
        user_id = created_user["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200

        retrieved_user = response.json()
        assert retrieved_user["id"] == user_id
        assert retrieved_user["name"] == "Test User"

    def test_event_creation_and_registration(self):
        """Test event management functionality"""
        # Create an event
        event_data = {
            "name": "Test AI Conference",
            "description": "A test conference for AI enthusiasts",
            "date": "2025-09-15T10:00:00",
            "location": "Test Center",
            "venue": "Test Venue",
            "city": "Test City",
            "country": "Test Country",
            "max_attendees": 100,
            "event_type": "conference"
        }

        response = client.post("/api/v1/events", json=event_data)
        assert response.status_code == 201

        created_event = response.json()
        assert created_event["name"] == "Test AI Conference"
        assert created_event["attendee_count"] == 0

        # Create users for testing
        users = []
        for i in range(3):
            user_data = {
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "job_title": "AI Engineer",
                "company": "AI Corp",
                "industry": "Technology",
                "interests": ["AI", "Machine Learning"],
                "goals": ["Network", "Learn"]
            }
            response = client.post("/api/v1/users", json=user_data)
            assert response.status_code == 201
            users.append(response.json())

        # Register users for the event
        event_id = created_event["id"]
        for user in users:
            response = client.post(f"/api/v1/events/{event_id}/register/{user['id']}")
            assert response.status_code == 200

        # Check updated attendee count
        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 200
        assert response.json()["attendee_count"] == 3

    def test_recommendation_generation_with_sample_data(self):
        """Test AI recommendation functionality with sample data"""
        # Create sample data first
        db = TestingSessionLocal()
        try:
            stats = create_sample_data(force_recreate=True)
            assert stats['users'] > 0
        finally:
            db.close()

        # Test recommendation generation for event 1
        recommendation_request = {
            "event_id": 1,
            "max_recommendations": 5
        }

        response = client.post("/api/v1/recommendations/generate", json=recommendation_request)
        assert response.status_code == 200

        recommendations = response.json()
        assert recommendations["event_id"] == 1
        assert "recommendations" in recommendations

        # Verify recommendation structure if recommendations exist
        if recommendations["recommendations"]:
            first_user_recs = recommendations["recommendations"][0]
            assert "user_id" in first_user_recs
            assert "user_name" in first_user_recs
            assert "recommended_users" in first_user_recs

            if first_user_recs["recommended_users"]:
                first_rec = first_user_recs["recommended_users"][0]
                assert "similarity_score" in first_rec
                assert "confidence_level" in first_rec
                assert "reason" in first_rec
                assert 0 <= first_rec["similarity_score"] <= 1

    def test_clustering_analysis(self):
        """Test network clustering functionality"""
        # Ensure sample data exists
        db = TestingSessionLocal()
        try:
            create_sample_data(force_recreate=True)
        finally:
            db.close()

        # Test cluster analysis
        cluster_request = {
            "event_id": 1,
            "algorithm": "louvain",
            "min_cluster_size": 2
        }

        response = client.post("/api/v1/clustering/analyze", json=cluster_request)
        assert response.status_code == 200

        analysis = response.json()
        assert analysis["event_id"] == 1
        assert "clusters" in analysis
        assert "cluster_stats" in analysis
        assert analysis["algorithm_used"] == "louvain"

        # Test network visualization data
        response = client.get("/api/v1/clustering/network/1")
        assert response.status_code == 200

        network_data = response.json()
        assert "nodes" in network_data
        assert "edges" in network_data
        assert "metadata" in network_data

    def test_analytics_endpoints(self):
        """Test analytics functionality"""
        # Ensure sample data exists
        db = TestingSessionLocal()
        try:
            create_sample_data(force_recreate=True)
        finally:
            db.close()

        # Test event analytics
        response = client.get("/api/v1/analytics/event/1")
        assert response.status_code == 200

        analytics = response.json()
        assert "event_name" in analytics
        assert "attendee_count" in analytics
        assert "industry_distribution" in analytics

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        # Test non-existent user
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 404

        # Test non-existent event
        response = client.get("/api/v1/events/99999")
        assert response.status_code == 404

        # Test invalid recommendation request
        invalid_request = {"event_id": 99999}
        response = client.post("/api/v1/recommendations/generate", json=invalid_request)
        assert response.status_code == 404

    def test_end_to_end_workflow(self):
        """Test the complete workflow from user creation to recommendations"""
        print("\n🚀 Starting end-to-end workflow test...")

        # 1. Create multiple users with diverse profiles
        users_data = [
            {
                "name": "Alice AI",
                "email": "alice@ai.com",
                "job_title": "ML Engineer",
                "company": "AI Corp",
                "industry": "Technology",
                "bio": "Passionate about machine learning and AI applications",
                "interests": ["Machine Learning", "Python", "AI"],
                "goals": ["Learn new techniques", "Find collaborators"]
            },
            {
                "name": "Bob Data",
                "email": "bob@data.com",
                "job_title": "Data Scientist",
                "company": "Data Inc",
                "industry": "Technology",
                "bio": "Expert in data analysis and visualization",
                "interests": ["Data Science", "Python", "Statistics"],
                "goals": ["Network with peers", "Share knowledge"]
            },
            {
                "name": "Carol Tech",
                "email": "carol@tech.com",
                "job_title": "Software Engineer",
                "company": "Tech Solutions",
                "industry": "Technology",
                "bio": "Full-stack developer interested in AI integration",
                "interests": ["Software Development", "AI", "Web Development"],
                "goals": ["Learn AI", "Build network"]
            }
        ]

        created_users = []
        for user_data in users_data:
            response = client.post("/api/v1/users", json=user_data)
            assert response.status_code == 201
            created_users.append(response.json())

        print(f"✅ Created {len(created_users)} users")

        # 2. Create an event
        event_data = {
            "name": "Tech Networking Event",
            "description": "A networking event for tech professionals",
            "date": "2025-10-01T18:00:00",
            "location": "Tech Hub",
            "max_attendees": 50,
            "event_type": "networking"
        }

        response = client.post("/api/v1/events", json=event_data)
        assert response.status_code == 201
        event = response.json()

        print(f"✅ Created event: {event['name']}")

        # 3. Register all users for the event
        for user in created_users:
            response = client.post(f"/api/v1/events/{event['id']}/register/{user['id']}")
            assert response.status_code == 200

        print(f"✅ Registered {len(created_users)} users for event")

        # 4. Generate recommendations
        recommendation_request = {
            "event_id": event["id"],
            "max_recommendations": 5
        }

        response = client.post("/api/v1/recommendations/generate", json=recommendation_request)
        assert response.status_code == 200

        recommendations = response.json()
        print(f"✅ Generated recommendations for {recommendations['total_users']} users")

        # 5. Analyze clusters
        cluster_request = {
            "event_id": event["id"],
            "algorithm": "louvain"
        }

        response = client.post("/api/v1/clustering/analyze", json=cluster_request)
        assert response.status_code == 200

        cluster_analysis = response.json()
        print(f"✅ Analyzed clusters: {len(cluster_analysis['clusters'])} clusters found")

        # 6. Get analytics
        response = client.get(f"/api/v1/analytics/event/{event['id']}")
        assert response.status_code == 200

        analytics = response.json()
        print(f"✅ Retrieved analytics for {analytics['attendee_count']} attendees")

        print("\n🎉 End-to-end test completed successfully!")
        print("✅ All systems functioning correctly!")


def cleanup_test_db():
    """Clean up test database"""
    if os.path.exists("test.db"):
        os.remove("test.db")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    cleanup_test_db()
