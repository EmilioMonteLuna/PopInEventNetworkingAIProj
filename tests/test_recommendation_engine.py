import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, User, Event, EventAttendee, UserInterest, UserGoal
from services.recommendation_engine import RecommendationEngine

engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

@pytest.fixture
def db_session():
    session = Session()
    yield session
    session.close()

def test_generate_recommendations_basic(db_session):
    # Setup: create event and users with interests/goals
    event = Event(name="Rec Event", description="desc", date="2025-08-01T10:00:00", location="Toronto", venue="Venue", city="Toronto", country="Canada", max_attendees=10, event_type="Conference")
    db_session.add(event)
    db_session.commit()
    user1 = User(name="Eve", email="eve@example.com", job_title="Engineer", company="A", industry="Tech", bio="AI enthusiast", experience_years=2, linkedin_url="", created_at=None, updated_at=None)
    user2 = User(name="Frank", email="frank@example.com", job_title="Manager", company="B", industry="Tech", bio="Interested in AI", experience_years=3, linkedin_url="", created_at=None, updated_at=None)
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.add_all([
        EventAttendee(event_id=event.id, user_id=user1.id),
        EventAttendee(event_id=event.id, user_id=user2.id),
        UserInterest(user_id=user1.id, interest="AI"),
        UserInterest(user_id=user2.id, interest="AI"),
        UserGoal(user_id=user1.id, goal="Network"),
        UserGoal(user_id=user2.id, goal="Network")
    ])
    db_session.commit()
    engine = RecommendationEngine()
    recs = engine.generate_recommendations(db=db_session, event_id=event.id, target_user_id=user1.id, max_recommendations=5)
    assert isinstance(recs, list)
    assert any(r["recommended_user_id"] == user2.id for r in recs)

def test_generate_recommendations_no_matches(db_session):
    event = Event(name="Empty Event", description="desc", date="2025-08-01T10:00:00", location="Toronto", venue="Venue", city="Toronto", country="Canada", max_attendees=10, event_type="Conference")
    db_session.add(event)
    db_session.commit()
    user1 = User(name="Solo", email="solo@example.com", job_title="Engineer", company="A", industry="Tech", bio="Solo bio", experience_years=2, linkedin_url="", created_at=None, updated_at=None)
    db_session.add(user1)
    db_session.commit()
    db_session.add(EventAttendee(event_id=event.id, user_id=user1.id))
    db_session.commit()
    engine = RecommendationEngine()
    recs = engine.generate_recommendations(db=db_session, event_id=event.id, target_user_id=user1.id, max_recommendations=5)
    assert recs == []

def test_generate_recommendations_invalid_user(db_session):
    # Setup: create event and a user
    event = Event(name="Invalid User Event", description="desc", date="2025-08-01T10:00:00", location="Toronto", venue="Venue", city="Toronto", country="Canada", max_attendees=10, event_type="Conference")
    db_session.add(event)
    db_session.commit()
    user1 = User(name="Valid", email="valid@example.com", job_title="Engineer", company="A", industry="Tech", bio="Bio", experience_years=2, linkedin_url="", created_at=None, updated_at=None)
    db_session.add(user1)
    db_session.commit()
    db_session.add(EventAttendee(event_id=event.id, user_id=user1.id))
    db_session.commit()
    engine = RecommendationEngine()
    # Use a non-existent user ID
    recs = engine.generate_recommendations(db=db_session, event_id=event.id, target_user_id=9999, max_recommendations=5)
    assert recs == []

def test_generate_recommendations_invalid_event(db_session):
    # No such event exists
    engine = RecommendationEngine()
    recs = engine.generate_recommendations(db=db_session, event_id=9999, target_user_id=1, max_recommendations=5)
    assert recs == []

# Additional: test output structure for recommendations
def test_recommendation_output_structure(db_session):
    event = Event(name="Struct Event", description="desc", date="2025-08-01T10:00:00", location="Toronto", venue="Venue", city="Toronto", country="Canada", max_attendees=10, event_type="Conference")
    db_session.add(event)
    db_session.commit()
    user1 = User(name="Anna", email="anna@example.com", job_title="Engineer", company="A", industry="Tech", bio="AI", experience_years=2, linkedin_url="", created_at=None, updated_at=None)
    user2 = User(name="Ben", email="ben@example.com", job_title="Manager", company="B", industry="Tech", bio="AI", experience_years=3, linkedin_url="", created_at=None, updated_at=None)
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.add_all([
        EventAttendee(event_id=event.id, user_id=user1.id),
        EventAttendee(event_id=event.id, user_id=user2.id),
        UserInterest(user_id=user1.id, interest="AI"),
        UserInterest(user_id=user2.id, interest="AI"),
        UserGoal(user_id=user1.id, goal="Network"),
        UserGoal(user_id=user2.id, goal="Network")
    ])
    db_session.commit()
    engine = RecommendationEngine()
    recs = engine.generate_recommendations(db=db_session, event_id=event.id, target_user_id=user1.id, max_recommendations=5)
    if recs:
        rec = recs[0]
        assert "recommended_user_id" in rec
        assert "recommended_user_name" in rec
        assert "similarity_score" in rec
        assert "reason" in rec
