# Database Models for Event Networking AI System
"""
SQLAlchemy database models for the Event Networking AI system.
These models define the database schema and relationships.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Float, Boolean, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

# ════════════════════════════════════════════════════════════════════════════════
# USER MODELS
# ════════════════════════════════════════════════════════════════════════════════

class User(Base):
    """User/Attendee model"""
    __tablename__ = "users"
    
    # Primary key and basic info
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Professional information
    job_title = Column(String(255), index=True)
    company = Column(String(255), index=True)
    industry = Column(String(100), index=True)
    bio = Column(Text)
    experience_years = Column(Integer)
    linkedin_url = Column(String(500))
    
    # Profile metadata
    profile_completeness = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("EventAttendee", back_populates="user")
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("UserGoal", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', company='{self.company}')>"

class UserInterest(Base):
    """User interests and skills"""
    __tablename__ = "user_interests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interest = Column(String(100), nullable=False, index=True)
    proficiency_level = Column(String(20), default="intermediate")
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="interests")
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'interest', name='_user_interest_unique'),
        Index('idx_interest_proficiency', 'interest', 'proficiency_level'),
    )
    
    def __repr__(self):
        return f"<UserInterest(user_id={self.user_id}, interest='{self.interest}')>"

class UserGoal(Base):
    """User networking goals"""
    __tablename__ = "user_goals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal = Column(String(255), nullable=False)
    goal_type = Column(String(20), default="network", index=True)
    priority = Column(Integer, default=1)  # 1=high, 2=medium, 3=low
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    
    # Indexes
    __table_args__ = (
        Index('idx_goal_type_priority', 'goal_type', 'priority'),
    )
    
    def __repr__(self):
        return f"<UserGoal(user_id={self.user_id}, goal_type='{self.goal_type}')>"

# ════════════════════════════════════════════════════════════════════════════════
# EVENT MODELS
# ════════════════════════════════════════════════════════════════════════════════

class Event(Base):
    """Event model"""
    __tablename__ = "events"
    
    # Primary key and basic info
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Event details
    date = Column(DateTime, nullable=False, index=True)
    location = Column(String(255))
    venue = Column(String(255))
    city = Column(String(100), index=True)
    country = Column(String(100), index=True)
    
    # Event configuration
    max_attendees = Column(Integer)
    event_type = Column(String(50), default="conference", index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendees = relationship("EventAttendee", back_populates="event")
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', date='{self.date}')>"

class EventAttendee(Base):
    """Event attendee relationship (many-to-many between Users and Events)"""
    __tablename__ = "event_attendees"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Attendance details
    attendance_status = Column(String(20), default="registered", index=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    attended_at = Column(DateTime)
    
    # Relationships
    event = relationship("Event", back_populates="attendees")
    user = relationship("User", back_populates="events")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='_event_user_unique'),
        Index('idx_event_attendance', 'event_id', 'attendance_status'),
    )
    
    def __repr__(self):
        return f"<EventAttendee(event_id={self.event_id}, user_id={self.user_id})>"

# ════════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION MODELS
# ════════════════════════════════════════════════════════════════════════════════

class Recommendation(Base):
    """AI-generated networking recommendations"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True)
    
    # Recommendation details
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recommended_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # AI scoring and analysis
    similarity_score = Column(Float, nullable=False, index=True)
    confidence_level = Column(String(20), default="medium", index=True)
    reason = Column(Text)
    mutual_interests = Column(Text)  # JSON string of shared interests
    complementary_goals = Column(Text)  # JSON string of complementary goals
    
    # Recommendation metadata
    algorithm_version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'recommended_user_id', 'event_id', 
                        name='_user_recommendation_unique'),
        Index('idx_recommendation_score', 'event_id', 'similarity_score'),
        Index('idx_recommendation_confidence', 'event_id', 'confidence_level'),
    )
    
    def __repr__(self):
        return f"<Recommendation(user_id={self.user_id}, recommended_user_id={self.recommended_user_id}, score={self.similarity_score})>"

class RecommendationFeedback(Base):
    """User feedback on recommendations"""
    __tablename__ = "recommendation_feedback"
    
    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    rating = Column(Integer)  # 1-5 star rating
    feedback_type = Column(String(20), index=True)  # helpful, not_helpful, connected, etc.
    comment = Column(Text)
    did_connect = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_feedback_rating', 'recommendation_id', 'rating'),
    )

# ════════════════════════════════════════════════════════════════════════════════
# CLUSTERING AND NETWORK MODELS
# ════════════════════════════════════════════════════════════════════════════════

class NetworkCluster(Base):
    """Network clustering results"""
    __tablename__ = "network_clusters"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Clustering details
    algorithm_used = Column(String(50), nullable=False)
    cluster_id = Column(Integer, nullable=False)
    cluster_size = Column(Integer, nullable=False)
    cluster_strength = Column(Float, default=0.0)
    dominant_industry = Column(String(100))
    
    # Analysis metadata
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    algorithm_version = Column(String(20), default="1.0")
    
    # Indexes
    __table_args__ = (
        Index('idx_cluster_event', 'event_id', 'cluster_id'),
        Index('idx_cluster_algorithm', 'algorithm_used', 'analysis_timestamp'),
    )

class ClusterMembership(Base):
    """User membership in network clusters"""
    __tablename__ = "cluster_memberships"
    
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("network_clusters.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    
    # Membership details
    centrality_score = Column(Float, default=0.0)  # How central the user is in the cluster
    connection_count = Column(Integer, default=0)  # Number of connections within cluster
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('cluster_id', 'user_id', name='_cluster_user_unique'),
        Index('idx_membership_centrality', 'cluster_id', 'centrality_score'),
    )

# ════════════════════════════════════════════════════════════════════════════════
# ANALYTICS AND METRICS MODELS
# ════════════════════════════════════════════════════════════════════════════════

class EventMetrics(Base):
    """Event-level analytics and metrics"""
    __tablename__ = "event_metrics"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, unique=True)
    
    # Attendance metrics
    total_registered = Column(Integer, default=0)
    total_confirmed = Column(Integer, default=0)
    total_attended = Column(Integer, default=0)
    
    # Recommendation metrics
    total_recommendations = Column(Integer, default=0)
    avg_similarity_score = Column(Float, default=0.0)
    high_confidence_recommendations = Column(Integer, default=0)
    
    # Networking metrics
    total_connections_made = Column(Integer, default=0)
    avg_connections_per_user = Column(Float, default=0.0)
    network_density = Column(Float, default=0.0)
    
    # Clustering metrics
    total_clusters = Column(Integer, default=0)
    avg_cluster_size = Column(Float, default=0.0)
    modularity_score = Column(Float, default=0.0)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EventMetrics(event_id={self.event_id}, total_registered={self.total_registered})>"

class UserMetrics(Base):
    """User-level analytics and metrics"""
    __tablename__ = "user_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Profile metrics
    profile_completeness = Column(Float, default=0.0)
    interests_count = Column(Integer, default=0)
    goals_count = Column(Integer, default=0)
    
    # Activity metrics
    events_attended = Column(Integer, default=0)
    total_recommendations_received = Column(Integer, default=0)
    total_connections_made = Column(Integer, default=0)
    avg_recommendation_score = Column(Float, default=0.0)
    
    # Networking effectiveness
    connection_success_rate = Column(Float, default=0.0)  # Percentage of recommendations that led to connections
    network_centrality = Column(Float, default=0.0)  # How central the user is across all events
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserMetrics(user_id={self.user_id}, profile_completeness={self.profile_completeness})>"

# ════════════════════════════════════════════════════════════════════════════════
# SYSTEM AND CONFIGURATION MODELS
# ════════════════════════════════════════════════════════════════════════════════

class SystemConfig(Base):
    """System configuration and settings"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string")  # string, int, float, boolean, json
    description = Column(Text)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value[:50]}...')>"

class ApiLog(Base):
    """API request logging for analytics and debugging"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True)
    
    # Request details
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    
    # Response details
    status_code = Column(Integer, index=True)
    response_time_ms = Column(Integer)
    error_message = Column(Text)
    
    # Request metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_api_log_endpoint_time', 'endpoint', 'timestamp'),
        Index('idx_api_log_status_time', 'status_code', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<ApiLog(endpoint='{self.endpoint}', status_code={self.status_code})>"

# ════════════════════════════════════════════════════════════════════════════════
# PERFORMANCE INDEXES
# ════════════════════════════════════════════════════════════════════════════════

# Additional indexes for performance optimization
# These are created separately to ensure they're applied after table creation

def create_performance_indexes(engine):
    """Create additional performance indexes"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        # Composite indexes for common query patterns
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_company_industry 
            ON users(company, industry) WHERE is_active = true
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_event_date_active 
            ON events(date, is_active) WHERE is_active = true
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recommendation_event_score 
            ON recommendations(event_id, similarity_score DESC) 
            WHERE is_active = true
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_interests_category 
            ON user_interests(interest, category)
        """))
        
        conn.commit()