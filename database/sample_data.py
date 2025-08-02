"""
Sample Data Generator for Event Networking AI System
Creates realistic test data for users, events, and relationships
"""
import logging
from datetime import datetime, timedelta
from typing import Dict

from sqlalchemy.orm import sessionmaker

from database.connection import create_database_engine as get_engine
from models.database import User, Event, EventAttendee, UserInterest, UserGoal

logger = logging.getLogger(__name__)


def create_sample_data(force_recreate: bool = False) -> Dict[str, int]:
    """Create comprehensive sample data for testing"""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if data already exists
        if not force_recreate and db.query(User).count() > 0:
            logger.info("Sample data already exists. Use force_recreate=True to recreate.")
            return {"users": db.query(User).count(), "events": db.query(Event).count()}

        # Clear existing data if recreating
        if force_recreate:
            db.query(EventAttendee).delete()
            db.query(UserGoal).delete()
            db.query(UserInterest).delete()
            db.query(User).delete()
            db.query(Event).delete()
            db.commit()
            logger.info("Cleared existing sample data")

        # Sample users with diverse profiles
        users_data = [
            {
                'name': 'Alice Johnson',
                'email': 'alice@techcorp.com',
                'job_title': 'ML Engineer',
                'company': 'TechCorp',
                'industry': 'Technology',
                'bio': 'Passionate about AI applications in healthcare and finance. Looking to collaborate on innovative ML projects.',
                'experience_years': 5,
                'linkedin_url': 'https://linkedin.com/in/alice-johnson',
                'interests': ['Machine Learning', 'Healthcare AI', 'Neural Networks', 'Python', 'Deep Learning'],
                'goals': ['Learn new techniques', 'Find collaborators', 'Share knowledge', 'Build network']
            },
            {
                'name': 'Bob Smith',
                'email': 'bob@aistartup.com',
                'job_title': 'Data Scientist',
                'company': 'AI Startup',
                'industry': 'Technology',
                'bio': 'Expert in computer vision and deep learning applications. Experienced in building scalable ML pipelines.',
                'experience_years': 3,
                'linkedin_url': 'https://linkedin.com/in/bob-smith',
                'interests': ['Computer Vision', 'Deep Learning', 'Image Processing', 'TensorFlow', 'PyTorch'],
                'goals': ['Network with peers', 'Find job opportunities', 'Learn trends', 'Share expertise']
            },
            {
                'name': 'Carol Davis',
                'email': 'carol@techconsulting.com',
                'job_title': 'AI Consultant',
                'company': 'Tech Consulting',
                'industry': 'Consulting',
                'bio': 'Helping companies implement AI solutions and strategies. 10+ years in technology consulting.',
                'experience_years': 8,
                'linkedin_url': 'https://linkedin.com/in/carol-davis',
                'interests': ['AI Strategy', 'Machine Learning', 'Business Intelligence', 'Consulting',
                              'Digital Transformation'],
                'goals': ['Find clients', 'Share expertise', 'Learn new applications', 'Build partnerships']
            },
            {
                'name': 'David Wilson',
                'email': 'david@techcorp.com',
                'job_title': 'Product Manager',
                'company': 'TechCorp',
                'industry': 'Technology',
                'bio': 'Managing AI product development and go-to-market strategies. Bridge between tech and business.',
                'experience_years': 7,
                'linkedin_url': 'https://linkedin.com/in/david-wilson',
                'interests': ['Product Strategy', 'AI Applications', 'Market Analysis', 'User Experience', 'Agile'],
                'goals': ['Network with engineers', 'Learn technical trends', 'Find partners',
                          'Understand market needs']
            },
            {
                'name': 'Eve Chen',
                'email': 'eve@innovativeai.com',
                'job_title': 'Research Scientist',
                'company': 'Innovative AI',
                'industry': 'Research',
                'bio': 'Researching next-generation AI algorithms and applications. PhD in Computer Science.',
                'experience_years': 4,
                'linkedin_url': 'https://linkedin.com/in/eve-chen',
                'interests': ['AI Research', 'Algorithm Development', 'Scientific Computing', 'NLP',
                              'Reinforcement Learning'],
                'goals': ['Present research', 'Find collaborators', 'Learn from peers', 'Publish papers']
            },
            {
                'name': 'Frank Martinez',
                'email': 'frank@datadriven.com',
                'job_title': 'Data Engineer',
                'company': 'Data Driven',
                'industry': 'Technology',
                'bio': 'Building scalable data pipelines and ML infrastructure. Expert in cloud technologies.',
                'experience_years': 6,
                'linkedin_url': 'https://linkedin.com/in/frank-martinez',
                'interests': ['Data Engineering', 'MLOps', 'Cloud Computing', 'Kubernetes', 'Apache Spark'],
                'goals': ['Learn best practices', 'Network with data professionals', 'Share experience',
                          'Find opportunities']
            }
        ]

        # Create users
        db_users = []
        for user_data in users_data:
            db_user = User(
                name=user_data['name'],
                email=user_data['email'],
                job_title=user_data['job_title'],
                company=user_data['company'],
                industry=user_data['industry'],
                bio=user_data['bio'],
                experience_years=user_data['experience_years'],
                linkedin_url=user_data['linkedin_url']
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            db_users.append(db_user)

            # Add interests
            for interest in user_data['interests']:
                db_interest = UserInterest(
                    user_id=db_user.id,
                    interest=interest,
                    proficiency_level='advanced'
                )
                db.add(db_interest)

            # Add goals
            for goal in user_data['goals']:
                db_goal = UserGoal(
                    user_id=db_user.id,
                    goal=goal,
                    goal_type='network'
                )
                db.add(db_goal)

        db.commit()

        # Create sample events
        events_data = [
            {
                'name': 'AI Conference 2025',
                'description': 'Annual AI and Machine Learning Conference featuring the latest research and industry applications',
                'date': datetime.now() + timedelta(days=30),
                'location': 'San Francisco Convention Center',
                'venue': 'Main Auditorium',
                'city': 'San Francisco',
                'country': 'USA',
                'max_attendees': 500,
                'event_type': 'conference'
            },
            {
                'name': 'Tech Startup Summit',
                'description': 'Networking event for entrepreneurs, investors, and tech professionals',
                'date': datetime.now() + timedelta(days=45),
                'location': 'Austin Convention Center',
                'venue': 'Exhibition Hall',
                'city': 'Austin',
                'country': 'USA',
                'max_attendees': 300,
                'event_type': 'networking'
            }
        ]

        db_events = []
        for event_data in events_data:
            db_event = Event(
                name=event_data['name'],
                description=event_data['description'],
                date=event_data['date'],
                location=event_data['location'],
                venue=event_data['venue'],
                city=event_data['city'],
                country=event_data['country'],
                max_attendees=event_data['max_attendees'],
                event_type=event_data['event_type']
            )
            db.add(db_event)
            db.commit()
            db.refresh(db_event)
            db_events.append(db_event)

        # Register users for events (all users for first event)
        for user in db_users:
            registration = EventAttendee(
                event_id=db_events[0].id,  # AI Conference
                user_id=user.id,
                attendance_status='registered'
            )
            db.add(registration)

        # Register some users for second event
        for user in db_users[:4]:
            registration = EventAttendee(
                event_id=db_events[1].id,  # Tech Summit
                user_id=user.id,
                attendance_status='registered'
            )
            db.add(registration)

        db.commit()

        stats = {
            'users': len(db_users),
            'events': len(db_events),
            'interests': sum(len(user_data['interests']) for user_data in users_data),
            'goals': sum(len(user_data['goals']) for user_data in users_data),
            'registrations': len(db_users) + 4  # All users in event 1 + 4 users in event 2
        }

        logger.info(f"Sample data created successfully: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data(force_recreate=True)
