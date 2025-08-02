"""
Helper Utilities for Event Networking AI System
Common utility functions and helpers
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional,Tuple
from datetime import datetime
import logging
import re


logger = logging.getLogger(__name__)


def format_datetime(dt: datetime) -> str:
    """Format datetime for API responses"""
    return dt.isoformat() if dt else None


def calculate_recommendation_confidence(similarity_score: float) -> str:
    """Calculate confidence level for recommendations"""
    if similarity_score >= 0.8:
        return "very_high"
    elif similarity_score >= 0.6:
        return "high"
    elif similarity_score >= 0.4:
        return "medium"
    else:
        return "low"


def generate_color_palette(n_colors: int) -> List[str]:
    """Generate a colour palette for visualisation"""
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#AED6F1', '#F1948A', '#D2B4DE'
    ]

    # Repeat colors if needed
    while len(colors) < n_colors:
        colors.extend(colors)

    return colors[:n_colors]


def export_to_csv(data: List[Dict], filename: str = None) -> str:
    """Export data to CSV format"""
    try:
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)

        if filename:
            df.to_csv(filename, index=False)
            logger.info(f"Data exported to {filename}")

        return csv_content

    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return ""


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_text(text: str) -> str:
    """Sanitize text input"""
    if not text:
        return ""

    # Remove extra whitespaces and clean
    text = ' '.join(text.split())
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    return text.strip()


def calculate_profile_score(user_data: Dict) -> float:
    """Calculate user profile completeness score"""
    score = 0
    total_fields = 7

    # Check each field
    if user_data.get('name'):
        score += 1
    if user_data.get('email'):
        score += 1
    if user_data.get('job_title'):
        score += 1
    if user_data.get('company'):
        score += 1
    if user_data.get('industry'):
        score += 1
    if user_data.get('bio'):
        score += 1
    if user_data.get('experience_years') is not None:
        score += 1

    return round((score / total_fields) * 100, 2)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text using simple frequency analysis"""
    if not text:
        return []

    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # Common stop words to filter out
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did',
        'she', 'use', 'her', 'way', 'many', 'than', 'them', 'well', 'were'
    }

    # Filter and count
    filtered_words = [word for word in words if word not in stop_words]
    word_freq = pd.Series(filtered_words).value_counts()

    return word_freq.head(max_keywords).index.tolist()


class Timer:
    """Simple timer context manager"""

    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, *args):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        logger.info(f"{self.description} completed in {duration:.2f} seconds")


def format_similarity_reason(user1_data: Dict, user2_data: Dict, score: float) -> str:
    """Format a human-readable similarity reason"""
    reasons = []

    # Check for common interests
    interests1 = set((user1_data.get('interests', '') or '').lower().split(', '))
    interests2 = set((user2_data.get('interests', '') or '').lower().split(', '))
    common_interests = interests1 & interests2
    if common_interests and '' not in common_interests:
        reasons.append(f"Shared interests: {', '.join(list(common_interests)[:2])}")

    # Check for the same industry
    if (user1_data.get('industry') and user2_data.get('industry') and
            user1_data['industry'].lower() == user2_data['industry'].lower()):
        reasons.append(f"Both work in {user1_data['industry']}")

    # Check for a similar experience
    exp1 = user1_data.get('experience_years', 0) or 0
    exp2 = user2_data.get('experience_years', 0) or 0
    if abs(exp1 - exp2) <= 2:
        reasons.append("Similar experience levels")

    # Default reason
    if not reasons:
        reasons.append(f"High compatibility score ({score:.2f})")

    return "; ".join(reasons)


def validate_recommendation_request(request_data: Dict) -> Tuple[bool, List[str]]:
    """Validate recommendation request data"""
    errors = []

    if not request_data.get('event_id'):
        errors.append("Event ID is required")

    if request_data.get('max_recommendations', 0) > 20:
        errors.append("Maximum recommendations cannot exceed 20")

    if request_data.get('max_recommendations', 0) < 1:
        errors.append("Maximum recommendations must be at least 1")

    return len(errors) == 0, errors


def normalize_text_for_matching(text: str) -> str:
    """Normalize text for better matching"""
    if not text:
        return ""

    # Convert to lowercase and remove extra spaces
    text = text.lower().strip()

    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)

    # Remove extra whitespaces
    text = ' '.join(text.split())

    return text
