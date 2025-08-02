# AI Recommendation Engine for Event Networking System
"""
Core machine learning recommendation engine using TF-IDF vectorization and
cosine similarity to suggest meaningful connections between event attendees.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple, Optional
import logging
from sqlalchemy.orm import Session
import json

from models.database import User, Event, EventAttendee, UserInterest, UserGoal, Recommendation
from utils.helpers import calculate_recommendation_confidence, Timer

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """
    AI-powered recommendation engine for event networking
    Uses collaborative filtering and content-based approaches
    """
    
    def __init__(self, 
                 max_features: int = 1000,
                 min_similarity_threshold: float = 0.1,
                 ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize the recommendation engine
        
        Args:
            max_features: Maximum number of TF-IDF features
            min_similarity_threshold: Minimum similarity score for recommendations
            ngram_range: N-gram range for TF-IDF vectorizer
        """
        self.max_features = max_features
        self.min_similarity_threshold = min_similarity_threshold
        self.ngram_range = ngram_range
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words='english',
            ngram_range=self.ngram_range,
            lowercase=True,
            strip_accents='unicode',
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9]*\b'
        )
        
        # Initialize scaler for numerical features
        self.scaler = StandardScaler()
        
    def get_event_attendees_data(self, db: Session, event_id: int) -> pd.DataFrame:
        """
        Retrieve and prepare attendee data for recommendation processing
        
        Args:
            db: Database session
            event_id: ID of the event
            
        Returns:
            DataFrame with attendee information
        """
        try:
            # Query attendees with their profile information
            query = db.query(
                User.id.label('user_id'),
                User.name,
                User.job_title,
                User.company,
                User.industry,
                User.bio,
                User.experience_years
            ).join(EventAttendee).filter(EventAttendee.event_id == event_id)
            
            attendees = query.all()
            
            if not attendees:
                logger.warning(f"No attendees found for event {event_id}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'user_id': a.user_id,
                'name': a.name,
                'job_title': a.job_title or '',
                'company': a.company or '',
                'industry': a.industry or '',
                'bio': a.bio or '',
                'experience_years': a.experience_years or 0
            } for a in attendees])
            
            # Enrich with interests and goals
            for idx, row in df.iterrows():
                user_id = row['user_id']
                
                # Get user interests
                interests = db.query(UserInterest.interest).filter(
                    UserInterest.user_id == user_id
                ).all()
                df.at[idx, 'interests'] = ', '.join([i.interest for i in interests])
                
                # Get user goals
                goals = db.query(UserGoal.goal).filter(
                    UserGoal.user_id == user_id
                ).all()
                df.at[idx, 'goals'] = ', '.join([g.goal for g in goals])
            
            logger.info(f"Retrieved {len(df)} attendees for event {event_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving attendee data: {str(e)}")
            return pd.DataFrame()
    
    def create_user_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Create feature vectors for users using TF-IDF and numerical features
        
        Args:
            df: DataFrame with user information
            
        Returns:
            Combined feature matrix
        """
        if df.empty:
            return np.array([])
        
        try:
            # Combine text features for each user
            text_features = []
            for _, row in df.iterrows():
                # Combine all textual information
                combined_text = ' '.join([
                    str(row.get('job_title', '')),
                    str(row.get('company', '')),
                    str(row.get('industry', '')),
                    str(row.get('bio', '')),
                    str(row.get('interests', '')),
                    str(row.get('goals', ''))
                ]).strip()
                
                text_features.append(combined_text if combined_text else ' ')
            
            # Vectorize text features using TF-IDF
            text_vectors = self.vectorizer.fit_transform(text_features)
            
            # Create numerical features
            numerical_features = []
            for _, row in df.iterrows():
                exp_years = row.get('experience_years', 0) or 0
                # Normalize experience years (0-40 scale)
                normalized_exp = min(exp_years / 40.0, 1.0)
                numerical_features.append([normalized_exp])
            
            numerical_features = np.array(numerical_features)
            
            # Combine text and numerical features
            text_dense = text_vectors.toarray()
            combined_features = np.hstack([text_dense, numerical_features])
            
            logger.info(f"Created feature matrix of shape {combined_features.shape}")
            return combined_features
            
        except Exception as e:
            logger.error(f"Error creating user features: {str(e)}")
            return np.array([])
    
    def calculate_similarity_matrix(self, features: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity matrix between users
        
        Args:
            features: Feature matrix
            
        Returns:
            Similarity matrix
        """
        if features.size == 0:
            return np.array([])
        
        try:
            similarity_matrix = cosine_similarity(features)
            logger.info(f"Calculated similarity matrix of shape {similarity_matrix.shape}")
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Error calculating similarity matrix: {str(e)}")
            return np.array([])
    
    def generate_recommendations(self, 
                               db: Session, 
                               event_id: int,
                               target_user_id: Optional[int] = None,
                               max_recommendations: int = 10) -> List[Dict]:
        """
        Generate AI-powered networking recommendations
        
        Args:
            db: Database session
            event_id: ID of the event
            target_user_id: Specific user ID (optional, generates for all if None)
            max_recommendations: Maximum recommendations per user
            
        Returns:
            List of recommendation dictionaries
        """
        try:
            with Timer("Recommendation generation"):
                # Get attendee data
                df = self.get_event_attendees_data(db, event_id)
                
                if df.empty or len(df) < 2:
                    logger.warning(f"Insufficient attendees for recommendations in event {event_id}")
                    return []
                
                # Create feature vectors
                features = self.create_user_features(df)
                if features.size == 0:
                    logger.error("Failed to create feature vectors")
                    return []
                
                # Calculate similarity matrix
                similarity_matrix = self.calculate_similarity_matrix(features)
                if similarity_matrix.size == 0:
                    logger.error("Failed to calculate similarity matrix")
                    return []
                
                # Generate recommendations
                recommendations = []
                
                if target_user_id:
                    # Generate for specific user
                    user_indices = df[df['user_id'] == target_user_id].index
                    if len(user_indices) == 0:
                        logger.warning(f"User {target_user_id} not found in event {event_id}")
                        return []
                    
                    user_recommendations = self._generate_user_recommendations(
                        df, similarity_matrix, user_indices[0], max_recommendations
                    )
                    recommendations.extend(user_recommendations)
                else:
                    # Generate for all users
                    for idx in range(len(df)):
                        user_recommendations = self._generate_user_recommendations(
                            df, similarity_matrix, idx, max_recommendations
                        )
                        recommendations.extend(user_recommendations)
                
                # Save recommendations to database
                self._save_recommendations_to_db(db, event_id, recommendations)
                
                logger.info(f"Generated {len(recommendations)} recommendations for event {event_id}")
                return recommendations
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _generate_user_recommendations(self, 
                                     df: pd.DataFrame,
                                     similarity_matrix: np.ndarray,
                                     user_idx: int,
                                     max_recommendations: int) -> List[Dict]:
        """
        Generate recommendations for a specific user
        
        Args:
            df: DataFrame with user data
            similarity_matrix: Precomputed similarity matrix
            user_idx: Index of the user in the DataFrame
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of recommendations for the user
        """
        try:
            user_similarities = similarity_matrix[user_idx]
            user_data = df.iloc[user_idx]
            
            # Create recommendations for other users
            recommendations = []
            for other_idx, similarity_score in enumerate(user_similarities):
                # Skip self and low similarity scores
                if other_idx != user_idx and similarity_score > self.min_similarity_threshold:
                    other_user = df.iloc[other_idx]
                    
                    # Calculate confidence level
                    confidence_level = calculate_recommendation_confidence(similarity_score)
                    
                    # Generate explanation
                    reason, mutual_interests, complementary_goals = self._generate_recommendation_explanation(
                        user_data, other_user, similarity_score
                    )
                    
                    recommendation = {
                        'user_id': int(user_data['user_id']),
                        'user_name': user_data['name'],
                        'recommended_user_id': int(other_user['user_id']),
                        'recommended_user_name': other_user['name'],
                        'recommended_user_company': other_user['company'],
                        'recommended_user_title': other_user['job_title'],
                        'similarity_score': float(similarity_score),
                        'confidence_level': confidence_level,
                        'reason': reason,
                        'mutual_interests': mutual_interests,
                        'complementary_goals': complementary_goals
                    }
                    
                    recommendations.append(recommendation)
            
            # Sort by similarity score and return top N
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error generating user recommendations: {str(e)}")
            return []
    
    def _generate_recommendation_explanation(self, 
                                           user1: pd.Series, 
                                           user2: pd.Series,
                                           similarity_score: float) -> Tuple[str, List[str], List[str]]:
        """
        Generate human-readable explanation for recommendation
        
        Args:
            user1, user2: User data series
            similarity_score: Calculated similarity score
            
        Returns:
            Tuple of (reason string, mutual interests, complementary goals)
        """
        try:
            reasons = []
            mutual_interests = []
            complementary_goals = []
            
            # Check industry match
            if user1.get('industry') and user1['industry'] == user2.get('industry'):
                reasons.append(f"Both work in {user1['industry']}")
            
            # Check company match
            if user1.get('company') and user1['company'] == user2.get('company'):
                reasons.append(f"Both work at {user1['company']}")
            
            # Check experience level similarity
            exp1 = user1.get('experience_years', 0) or 0
            exp2 = user2.get('experience_years', 0) or 0
            if abs(exp1 - exp2) <= 3:
                reasons.append("Similar experience levels")
            
            # Analyze interests overlap
            interests1 = set((user1.get('interests', '') or '').lower().split(', '))
            interests2 = set((user2.get('interests', '') or '').lower().split(', '))
            interests1.discard('')  # Remove empty strings
            interests2.discard('')
            
            common_interests = interests1.intersection(interests2)
            if common_interests:
                mutual_interests = list(common_interests)[:3]  # Top 3
                reasons.append(f"Shared interests: {', '.join(mutual_interests[:2])}")
            
            # Analyze complementary goals
            goals1 = set((user1.get('goals', '') or '').lower().split(', '))
            goals2 = set((user2.get('goals', '') or '').lower().split(', '))
            goals1.discard('')
            goals2.discard('')
            
            # Look for complementary patterns (learn/teach, hire/job search)
            if 'learn' in goals1 and 'teach' in goals2:
                complementary_goals.append("Learning/Teaching match")
            if 'teach' in goals1 and 'learn' in goals2:
                complementary_goals.append("Teaching/Learning match")
            if 'hire' in goals1 and 'job search' in goals2:
                complementary_goals.append("Hiring/Job seeking match")
            if 'job search' in goals1 and 'hire' in goals2:
                complementary_goals.append("Job seeking/Hiring match")
            
            if complementary_goals:
                reasons.append("Complementary networking goals")
            
            # Fallback reason
            if not reasons:
                if similarity_score >= 0.7:
                    reasons.append("Strong profile compatibility")
                elif similarity_score >= 0.5:
                    reasons.append("Good profile match")
                else:
                    reasons.append("Potential networking opportunity")
            
            final_reason = "; ".join(reasons)
            return final_reason, mutual_interests, complementary_goals
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return f"High compatibility ({similarity_score:.2f})", [], []
    
    def _save_recommendations_to_db(self, 
                                  db: Session, 
                                  event_id: int,
                                  recommendations: List[Dict]) -> None:
        """
        Save generated recommendations to database
        
        Args:
            db: Database session
            event_id: Event ID
            recommendations: List of recommendation dictionaries
        """
        try:
            # Clear existing recommendations for this event
            db.query(Recommendation).filter(
                Recommendation.event_id == event_id
            ).delete()
            
            # Insert new recommendations
            for rec in recommendations:
                db_recommendation = Recommendation(
                    user_id=rec['user_id'],
                    recommended_user_id=rec['recommended_user_id'],
                    event_id=event_id,
                    similarity_score=rec['similarity_score'],
                    confidence_level=rec['confidence_level'],
                    reason=rec['reason'],
                    mutual_interests=json.dumps(rec['mutual_interests']),
                    complementary_goals=json.dumps(rec['complementary_goals']),
                    algorithm_version="1.0"
                )
                db.add(db_recommendation)
            
            db.commit()
            logger.info(f"Saved {len(recommendations)} recommendations to database")
            
        except Exception as e:
            logger.error(f"Error saving recommendations to database: {str(e)}")
            db.rollback()
    
    def get_user_recommendations(self, 
                               db: Session,
                               user_id: int,
                               event_id: int,
                               limit: int = 10) -> List[Dict]:
        """
        Retrieve saved recommendations for a user
        
        Args:
            db: Database session
            user_id: User ID
            event_id: Event ID
            limit: Maximum number of recommendations
            
        Returns:
            List of recommendations
        """
        try:
            recommendations = db.query(Recommendation).filter(
                Recommendation.user_id == user_id,
                Recommendation.event_id == event_id,
                Recommendation.is_active == True
            ).order_by(Recommendation.similarity_score.desc()).limit(limit).all()
            
            result = []
            for rec in recommendations:
                # Get recommended user details
                user = db.query(User).filter(User.id == rec.recommended_user_id).first()
                if user:
                    result.append({
                        'recommended_user_id': rec.recommended_user_id,
                        'recommended_user_name': user.name,
                        'recommended_user_company': user.company,
                        'recommended_user_title': user.job_title,
                        'similarity_score': rec.similarity_score,
                        'confidence_level': rec.confidence_level,
                        'reason': rec.reason,
                        'mutual_interests': json.loads(rec.mutual_interests) if rec.mutual_interests else [],
                        'complementary_goals': json.loads(rec.complementary_goals) if rec.complementary_goals else []
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving user recommendations: {str(e)}")
            return []