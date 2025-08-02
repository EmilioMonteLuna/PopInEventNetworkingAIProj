"""
API Routes for Event Networking AI System
FastAPI endpoints for user management, events, recommendations, and clustering
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import networkx as nx

from database.connection import get_db
from models.schemas import (
    UserCreate, UserProfile, EventCreate, EventInfo,
    RecommendationRequest, BulkRecommendationResponse,
    ClusterAnalysisRequest, ClusterAnalysisResponse,
    NetworkData, SuccessResponse, HealthCheck, EventAnalytics, UserAnalytics
)
from models.database import User, Event, EventAttendee, UserInterest, UserGoal
from services.recommendation_engine import RecommendationEngine
from services.clustering_service import ClusteringService
from services.data_service import DataService
from fastapi.responses import JSONResponse
import plotly

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
recommendation_engine = RecommendationEngine()
clustering_service = ClusteringService()
data_service = DataService()


# ════════════════════════════════════════════════════════════════════════════════
# HEALTH AND SYSTEM ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """System health check endpoint"""
    return HealthCheck(
        status="healthy",
        service="Event Networking AI",
        version="1.0.0",
        database_status="connected",
        ml_engine_status="ready",
        dependencies_status={
            "scikit_learn": "operational",
            "networkx": "operational",
            "pandas": "operational"
        }
    )


# ════════════════════════════════════════════════════════════════════════════════
# USER MANAGEMENT ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/users", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user profile"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create user
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            job_title=user_data.job_title,
            company=user_data.company,
            industry=user_data.industry,
            bio=user_data.bio,
            experience_years=user_data.experience_years,
            linkedin_url=user_data.linkedin_url
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Add interests
        for interest in user_data.interests:
            db_interest = UserInterest(user_id=db_user.id, interest=interest)
            db.add(db_interest)

        # Add goals
        for goal in user_data.goals:
            db_goal = UserGoal(user_id=db_user.id, goal=goal)
            db.add(db_goal)

        db.commit()

        return UserProfile(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            job_title=db_user.job_title,
            company=db_user.company,
            industry=db_user.industry,
            bio=db_user.bio,
            experience_years=db_user.experience_years,
            linkedin_url=db_user.linkedin_url,
            interests=user_data.interests,
            goals=user_data.goals,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get interests and goals
        interests = [i.interest for i in user.interests]
        goals = [g.goal for g in user.goals]

        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            job_title=user.job_title,
            company=user.company,
            industry=user.industry,
            bio=user.bio,
            experience_years=user.experience_years,
            linkedin_url=user.linkedin_url,
            interests=interests,
            goals=goals,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ════════════════════════════════════════════════════════════════════════════════
# EVENT MANAGEMENT ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/events", response_model=EventInfo, status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    try:
        db_event = Event(
            name=event_data.name,
            description=event_data.description,
            date=event_data.date,
            location=event_data.location,
            venue=event_data.venue,
            city=event_data.city,
            country=event_data.country,
            max_attendees=event_data.max_attendees,
            event_type=event_data.event_type
        )

        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return EventInfo(
            id=db_event.id,
            name=db_event.name,
            description=db_event.description,
            date=db_event.date,
            location=db_event.location,
            venue=db_event.venue,
            city=db_event.city,
            country=db_event.country,
            max_attendees=db_event.max_attendees,
            event_type=db_event.event_type,
            is_active=db_event.is_active,
            attendee_count=0,
            created_at=db_event.created_at
        )

    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/events/{event_id}", response_model=EventInfo)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get event information by ID"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        attendee_count = db.query(EventAttendee).filter(
            EventAttendee.event_id == event_id
        ).count()

        return EventInfo(
            id=event.id,
            name=event.name,
            description=event.description,
            date=event.date,
            location=event.location,
            venue=event.venue,
            city=event.city,
            country=event.country,
            max_attendees=event.max_attendees,
            event_type=event.event_type,
            is_active=event.is_active,
            attendee_count=attendee_count,
            created_at=event.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/events/{event_id}/register/{user_id}", response_model=SuccessResponse)
async def register_user_for_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    """Register a user for an event"""
    try:
        # Verify event and user exist
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if already registered
        existing = db.query(EventAttendee).filter(
            EventAttendee.event_id == event_id,
            EventAttendee.user_id == user_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="User already registered")

        # Create registration
        registration = EventAttendee(event_id=event_id, user_id=user_id)
        db.add(registration)
        db.commit()

        return SuccessResponse(
            message=f"User {user.name} successfully registered for {event.name}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ════════════════════════════════════════════════════════════════════════════════
# AI RECOMMENDATION ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/recommendations/generate", response_model=BulkRecommendationResponse)
async def generate_recommendations(
        request: RecommendationRequest,
        db: Session = Depends(get_db)
):
    """Generate AI-powered networking recommendations"""
    try:
        start_time = datetime.now()

        # Get event information
        event = db.query(Event).filter(Event.id == request.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Generate recommendations using ML engine
        recommendations = recommendation_engine.generate_recommendations(
            db=db,
            event_id=request.event_id,
            target_user_id=request.user_id,
            max_recommendations=request.max_recommendations
        )

        if not recommendations:
            return BulkRecommendationResponse(
                event_id=request.event_id,
                event_name=event.name,
                recommendations=[],
                total_users=0,
                generation_time_seconds=0.0,
                algorithm_info={"status": "no_recommendations_generated"}
            )

        # Group recommendations by user
        from collections import defaultdict
        user_recommendations = defaultdict(list)

        for rec in recommendations:
            user_id = rec['user_id']
            user_recommendations[user_id].append({
                'recommended_user_id': rec['recommended_user_id'],
                'recommended_user_name': rec['recommended_user_name'],
                'recommended_user_company': rec['recommended_user_company'],
                'recommended_user_title': rec['recommended_user_title'],
                'similarity_score': rec['similarity_score'],
                'confidence_level': rec['confidence_level'],
                'reason': rec['reason'],
                'mutual_interests': rec.get('mutual_interests', []),
                'complementary_goals': rec.get('complementary_goals', [])
            })

        # Format response
        formatted_recommendations = []
        for user_id, user_recs in user_recommendations.items():
            user_name = user_recs[0]['recommended_user_name'] if user_recs else "Unknown"
            formatted_recommendations.append({
                'user_id': user_id,
                'user_name': user_name,
                'total_recommendations': len(user_recs),
                'recommended_users': user_recs,
                'generated_at': datetime.now()
            })

        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()

        return BulkRecommendationResponse(
            event_id=request.event_id,
            event_name=event.name,
            recommendations=formatted_recommendations,
            total_users=len(formatted_recommendations),
            generation_time_seconds=generation_time,
            algorithm_info={
                "algorithm": "TF-IDF + Cosine Similarity",
                "version": "1.0",
                "features_used": ["bio", "interests", "goals", "job_title", "company", "industry"]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ════════════════════════════════════════════════════════════════════════════════
# CLUSTERING ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/clustering/analyze", response_model=ClusterAnalysisResponse)
async def analyze_clusters(
        request: ClusterAnalysisRequest,
        db: Session = Depends(get_db)
):
    """Perform network cluster analysis on event attendees"""
    try:
        result = clustering_service.analyze_clusters(
            db=db,
            event_id=request.event_id,
            algorithm=request.algorithm,
            min_cluster_size=request.min_cluster_size
        )

        return result

    except Exception as e:
        logger.error(f"Error analyzing clusters: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clustering/network/{event_id}", response_model=NetworkData)
async def get_network_data(event_id: int, db: Session = Depends(get_db)):
    """Get network visualization data for an event"""
    try:
        network_data = clustering_service.export_network_for_visualization(
            db=db,
            event_id=event_id
        )

        return network_data

    except Exception as e:
        logger.error(f"Error getting network data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/visualization/cluster-map", response_class=JSONResponse)
async def get_cluster_map(event_id: int, db: Session = Depends(get_db)):
    """Generate and return a cluster map visualization for an event as Plotly JSON."""
    try:
        G = clustering_service.create_network_graph(db, event_id)
        if G.number_of_nodes() == 0:
            return JSONResponse(content={"error": "No attendees or insufficient data for visualization."}, status_code=404)

        # Use spring layout for visualization
        pos = nx.spring_layout(G)
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        edge_trace = dict(type='scatter', x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#888'), hoverinfo='none')

        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(G.nodes[node].get('name', str(node)))
        node_trace = dict(type='scatter', x=node_x, y=node_y, mode='markers', hoverinfo='text', text=node_text, marker=dict(showscale=False, color='#1f77b4', size=12, line_width=2))

        fig = dict(data=[edge_trace, node_trace], layout=dict(showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0)))
        return JSONResponse(content=fig)
    except Exception as e:
        logger.error(f"Error generating cluster map: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cluster map.")


# ════════════════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/analytics/event/{event_id}", response_model=EventAnalytics)
async def get_event_analytics(event_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analytics for an event"""
    try:
        analytics = data_service.get_event_statistics(db=db, event_id=event_id)

        if not analytics:
            raise HTTPException(status_code=404, detail="Event not found")

        return EventAnalytics(**analytics)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/user/{user_id}", response_model=UserAnalytics)
async def get_user_analytics(user_id: int, db: Session = Depends(get_db)):
    """Get user profile analytics"""
    try:
        analytics = data_service.get_user_profile_completeness(db=db, user_id=user_id)

        if not analytics:
            raise HTTPException(status_code=404, detail="User not found")

        return UserAnalytics(**analytics)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
