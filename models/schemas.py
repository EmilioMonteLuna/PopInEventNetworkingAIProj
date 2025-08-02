# Pydantic Schemas for Event Networking AI System
"""
Pydantic models for API request/response validation and serialization.
These schemas define the structure of data exchanged through the API.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# ════════════════════════════════════════════════════════════════════════════════
# BASE MODELS AND ENUMS
# ════════════════════════════════════════════════════════════════════════════════

class ProficiencyLevel(str, Enum):
    """User proficiency levels for interests"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class GoalType(str, Enum):
    """Types of networking goals"""
    LEARN = "learn"
    TEACH = "teach"
    COLLABORATE = "collaborate"
    HIRE = "hire"
    JOB_SEARCH = "job_search"
    NETWORK = "network"

class ConfidenceLevel(str, Enum):
    """Confidence levels for recommendations"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ClusteringAlgorithm(str, Enum):
    """Available clustering algorithms"""
    LOUVAIN = "louvain"
    GIRVAN_NEWMAN = "girvan_newman"
    LABEL_PROPAGATION = "label_propagation"

class AttendanceStatus(str, Enum):
    """Event attendance status"""
    REGISTERED = "registered"
    CONFIRMED = "confirmed"
    ATTENDED = "attended"
    NO_SHOW = "no_show"

# ════════════════════════════════════════════════════════════════════════════════
# USER MODELS
# ════════════════════════════════════════════════════════════════════════════════

class UserInterestBase(BaseModel):
    """Base model for user interests"""
    interest: str = Field(..., min_length=1, max_length=100)
    proficiency_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE
    category: Optional[str] = Field(None, max_length=50)

class UserGoalBase(BaseModel):
    """Base model for user goals"""
    goal: str = Field(..., min_length=1, max_length=255)
    goal_type: GoalType = GoalType.NETWORK
    priority: int = Field(1, ge=1, le=3)

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    job_title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    interests: List[str] = Field(default_factory=list, max_items=20)
    goals: List[str] = Field(default_factory=list, max_items=10)
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('LinkedIn URL must be a valid URL')
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=2000)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    interests: Optional[List[str]] = Field(None, max_items=20)
    goals: Optional[List[str]] = Field(None, max_items=10)

class UserProfile(BaseModel):
    """Complete user profile schema"""
    id: int
    name: str
    email: str
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = None
    linkedin_url: Optional[str] = None
    profile_completeness: float
    interests: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserSummary(BaseModel):
    """Lightweight user summary for listings"""
    id: int
    name: str
    job_title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None

# ════════════════════════════════════════════════════════════════════════════════
# EVENT MODELS
# ════════════════════════════════════════════════════════════════════════════════

class EventCreate(BaseModel):
    """Schema for creating a new event"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    date: datetime
    location: Optional[str] = Field(None, max_length=255)
    venue: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    max_attendees: Optional[int] = Field(None, ge=1, le=10000)
    event_type: Optional[str] = Field("conference", max_length=50)
    
    @validator('date')
    def validate_future_date(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Event date must be in the future')
        return v

class EventUpdate(BaseModel):
    """Schema for updating event information"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    venue: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    max_attendees: Optional[int] = Field(None, ge=1, le=10000)
    event_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None

class EventInfo(BaseModel):
    """Complete event information schema"""
    id: int
    name: str
    description: Optional[str] = None
    date: datetime
    location: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    max_attendees: Optional[int] = None
    attendee_count: int
    is_active: bool
    event_type: str
    is_full: bool
    is_upcoming: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventSummary(BaseModel):
    """Lightweight event summary for listings"""
    id: int
    name: str
    date: datetime
    location: Optional[str] = None
    attendee_count: int
    is_active: bool

# ════════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION MODELS
# ════════════════════════════════════════════════════════════════════════════════

class RecommendationItem(BaseModel):
    """Individual recommendation item"""
    recommended_user_id: int
    recommended_user_name: str
    recommended_user_company: Optional[str] = None
    recommended_user_title: Optional[str] = None
    similarity_score: float = Field(..., ge=0, le=1)
    confidence_level: ConfidenceLevel
    reason: str
    mutual_interests: List[str] = Field(default_factory=list)
    complementary_goals: List[str] = Field(default_factory=list)

class RecommendationResponse(BaseModel):
    """Response containing recommendations for a single user"""
    user_id: int
    user_name: str
    total_recommendations: int
    recommended_users: List[RecommendationItem] = Field(default_factory=list)
    generated_at: datetime

class RecommendationRequest(BaseModel):
    """Request schema for generating recommendations"""
    event_id: int
    user_id: Optional[int] = None
    max_recommendations: int = Field(10, ge=1, le=20)
    min_similarity_threshold: Optional[float] = Field(None, ge=0, le=1)

class BulkRecommendationResponse(BaseModel):
    """Response containing recommendations for all users at an event"""
    event_id: int
    event_name: str
    recommendations: List[RecommendationResponse]
    total_users: int
    generation_time_seconds: float
    algorithm_info: Dict[str, Any]

# ════════════════════════════════════════════════════════════════════════════════
# CLUSTERING AND NETWORK MODELS
# ════════════════════════════════════════════════════════════════════════════════

class ClusterMember(BaseModel):
    """Member of a cluster in network analysis"""
    user_id: int
    name: str
    company: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    degree: int  # Number of connections in the network

class Cluster(BaseModel):
    """Cluster of similar users"""
    cluster_id: int
    size: int
    dominant_industry: Optional[str] = None
    cluster_strength: float = Field(..., ge=0, le=1)
    common_interests: List[str] = Field(default_factory=list)
    members: List[ClusterMember]

class ClusterAnalysisRequest(BaseModel):
    """Request for cluster analysis"""
    event_id: int
    algorithm: ClusteringAlgorithm = ClusteringAlgorithm.LOUVAIN
    min_cluster_size: int = Field(2, ge=2, le=50)
    similarity_threshold: Optional[float] = Field(None, ge=0, le=1)

class ClusterAnalysisResponse(BaseModel):
    """Response containing cluster analysis results"""
    event_id: int
    event_name: str
    algorithm_used: ClusteringAlgorithm
    clusters: List[Cluster]
    cluster_stats: Dict[str, Any]
    analysis_timestamp: datetime

class NetworkNode(BaseModel):
    """Node in the network visualization"""
    id: int
    name: str
    company: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None
    cluster: int
    degree: int
    size: int  # Visual size for rendering
    color: str  # Hex color code

class NetworkEdge(BaseModel):
    """Edge in the network visualization"""
    source: int
    target: int
    weight: float = Field(..., ge=0, le=1)
    similarity_type: str = "cosine_similarity"

class NetworkData(BaseModel):
    """Complete network data for visualization"""
    event_id: int
    nodes: List[NetworkNode]
    edges: List[NetworkEdge]
    metadata: Dict[str, Any]
    generated_at: datetime

# ════════════════════════════════════════════════════════════════════════════════
# ANALYTICS MODELS
# ════════════════════════════════════════════════════════════════════════════════

class EventAnalytics(BaseModel):
    """Analytics data for an event"""
    event_id: int
    event_name: str
    event_date: str
    attendee_count: int
    industry_distribution: Dict[str, int]
    company_distribution: Dict[str, int]
    experience_stats: Dict[str, float]
    top_interests: Dict[str, int]

class UserAnalytics(BaseModel):
    """Analytics data for a user profile"""
    user_id: int
    profile_completeness: float
    fields_status: Dict[str, bool]
    interests_count: int
    goals_count: int
    recommendations: List[str]

class RecommendationAnalytics(BaseModel):
    """Analytics for recommendation quality and performance"""
    event_id: int
    total_recommendations: int
    average_similarity_score: float
    confidence_distribution: Dict[str, int]
    common_recommendation_reasons: List[Dict[str, Any]]

# ════════════════════════════════════════════════════════════════════════════════
# SYSTEM AND UTILITY MODELS
# ════════════════════════════════════════════════════════════════════════════════

class HealthCheck(BaseModel):
    """System health check response"""
    status: str
    service: str
    version: str
    database_status: str
    ml_engine_status: str
    dependencies_status: Dict[str, str]

class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None
    success: bool = False

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# ════════════════════════════════════════════════════════════════════════════════
# DATA EXPORT MODELS
# ════════════════════════════════════════════════════════════════════════════════

class ExportFormat(str, Enum):
    """Available export formats"""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"

class ExportRequest(BaseModel):
    """Request for data export"""
    event_id: int
    format: ExportFormat = ExportFormat.JSON
    include_recommendations: bool = True
    include_clusters: bool = True
    include_analytics: bool = False

class ExportResponse(BaseModel):
    """Response for data export"""
    event_id: int
    format: ExportFormat
    download_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    generated_at: datetime
    expires_at: Optional[datetime] = None

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MODELS
# ════════════════════════════════════════════════════════════════════════════════

class SystemConfig(BaseModel):
    """System configuration information"""
    version: str
    algorithms: Dict[str, Any]
    limits: Dict[str, int]
    features: List[str]

class AlgorithmConfig(BaseModel):
    """Configuration for recommendation algorithms"""
    min_similarity_threshold: float = Field(0.1, ge=0, le=1)
    max_recommendations: int = Field(10, ge=1, le=50)
    tfidf_max_features: int = Field(1000, ge=100, le=10000)
    clustering_algorithm: ClusteringAlgorithm = ClusteringAlgorithm.LOUVAIN