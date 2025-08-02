"""
Data Processing Service for Event Networking AI System
Analytics, statistics, and data processing utilities
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from models.database import User, Event, EventAttendee, UserInterest, UserGoal, Recommendation

logger = logging.getLogger(__name__)


class DataService:
    """Data processing and analytics service"""

    @staticmethod
    def get_event_statistics(db: Session, event_id: int) -> Dict:
        """Get comprehensive statistics for an event"""
        try:
            # Basic event info
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return {"error": "Event not found"}

            # Attendee count
            attendee_count = db.query(EventAttendee).filter(
                EventAttendee.event_id == event_id
            ).count()

            # Industry distribution
            industry_query = db.query(
                User.industry,
                func.count(User.id).label('count')
            ).join(EventAttendee).filter(
                EventAttendee.event_id == event_id,
                User.industry.isnot(None)
            ).group_by(User.industry).all()

            industry_distribution = {
                item.industry: item.count for item in industry_query
            }

            # Company distribution
            company_query = db.query(
                User.company,
                func.count(User.id).label('count')
            ).join(EventAttendee).filter(
                EventAttendee.event_id == event_id,
                User.company.isnot(None)
            ).group_by(User.company).all()

            company_distribution = {
                item.company: item.count for item in company_query
            }

            # Experience distribution
            experience_query = db.query(User.experience_years).join(
                EventAttendee
            ).filter(
                EventAttendee.event_id == event_id,
                User.experience_years.isnot(None)
            ).all()

            experience_years = [e.experience_years for e in experience_query]
            experience_stats = {
                'min': min(experience_years) if experience_years else 0,
                'max': max(experience_years) if experience_years else 0,
                'avg': round(np.mean(experience_years), 1) if experience_years else 0,
                'median': np.median(experience_years) if experience_years else 0
            }

            # Top interests
            interests_query = db.query(
                UserInterest.interest,
                func.count(UserInterest.id).label('count')
            ).join(User).join(EventAttendee).filter(
                EventAttendee.event_id == event_id
            ).group_by(UserInterest.interest).order_by(
                func.count(UserInterest.id).desc()
            ).limit(10).all()

            top_interests = {
                item.interest: item.count for item in interests_query
            }

            return {
                'event_id': event_id,
                'event_name': event.name,
                'event_date': event.date.isoformat(),
                'attendee_count': attendee_count,
                'industry_distribution': industry_distribution,
                'company_distribution': company_distribution,
                'experience_stats': experience_stats,
                'top_interests': top_interests
            }

        except Exception as e:
            logger.error(f"Error getting event statistics: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_user_profile_completeness(db: Session, user_id: int) -> Dict:
        """Analyze user profile completeness"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}

            # Check profile fields
            completeness_score = 0
            total_fields = 7

            fields_status = {
                'name': bool(user.name),
                'email': bool(user.email),
                'job_title': bool(user.job_title),
                'company': bool(user.company),
                'industry': bool(user.industry),
                'bio': bool(user.bio),
                'experience_years': user.experience_years is not None
            }

            completeness_score = sum(fields_status.values())

            # Check interests and goals
            interests_count = db.query(UserInterest).filter(
                UserInterest.user_id == user_id
            ).count()

            goals_count = db.query(UserGoal).filter(
                UserGoal.user_id == user_id
            ).count()

            # Generate recommendations
            recommendations = []
            if not fields_status.get('bio'):
                recommendations.append("Add a professional bio")
            if interests_count < 3:
                recommendations.append("Add more interests (minimum 3)")
            if goals_count < 2:
                recommendations.append("Define networking goals")

            return {
                'user_id': user_id,
                'profile_completeness': round((completeness_score / total_fields) * 100, 2),
                'fields_status': fields_status,
                'interests_count': interests_count,
                'goals_count': goals_count,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"Error analyzing profile completeness: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_recommendation_analytics(db: Session, event_id: int) -> Dict:
        """Get analytics about recommendations for an event"""
        try:
            # Basic recommendation stats
            total_recommendations = db.query(Recommendation).filter(
                Recommendation.event_id == event_id,
                Recommendation.is_active == True
            ).count()

            if total_recommendations == 0:
                return {
                    "event_id": event_id,
                    "total_recommendations": 0,
                    "message": "No recommendations found"
                }

            # Average similarity score
            avg_similarity = db.query(
                func.avg(Recommendation.similarity_score)
            ).filter(
                Recommendation.event_id == event_id,
                Recommendation.is_active == True
            ).scalar()

            # Confidence distribution
            confidence_dist = db.query(
                Recommendation.confidence_level,
                func.count(Recommendation.id).label('count')
            ).filter(
                Recommendation.event_id == event_id,
                Recommendation.is_active == True
            ).group_by(Recommendation.confidence_level).all()

            confidence_distribution = {
                level: count for level, count in confidence_dist
            }

            return {
                "event_id": event_id,
                "total_recommendations": total_recommendations,
                "average_similarity_score": round(float(avg_similarity), 3) if avg_similarity else 0.0,
                "confidence_distribution": confidence_distribution
            }

        except Exception as e:
            logger.error(f"Error getting recommendation analytics: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def export_recommendations_to_csv(db: Session, event_id: int) -> str:
        """Export recommendations to CSV format"""
        try:
            # Get all recommendations for the event
            recommendations = db.query(
                Recommendation.user_id,
                Recommendation.recommended_user_id,
                Recommendation.similarity_score,
                Recommendation.confidence_level,
                Recommendation.reason
            ).filter(
                Recommendation.event_id == event_id,
                Recommendation.is_active == True
            ).all()

            if not recommendations:
                return ""

            # Convert to DataFrame and CSV
            df = pd.DataFrame([
                {
                    'user_id': rec.user_id,
                    'recommended_user_id': rec.recommended_user_id,
                    'similarity_score': rec.similarity_score,
                    'confidence_level': rec.confidence_level,
                    'reason': rec.reason
                }
                for rec in recommendations
            ])

            return df.to_csv(index=False)

        except Exception as e:
            logger.error(f"Error exporting recommendations: {str(e)}")
            return ""
