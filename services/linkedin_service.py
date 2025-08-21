"""
LinkedIn Integration Service
Handles OAuth authentication and LinkedIn API integration for profile data retrieval.
Based on LinkedIn's Get Profile API for professional networking enhancement.
"""

import requests
import logging
from typing import Optional, Dict, List
from urllib.parse import urlencode, parse_qs, urlparse
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import User, UserInterest, UserGoal

logger = logging.getLogger(__name__)


class LinkedInService:
    """
    LinkedIn API integration service for OAuth authentication and profile data retrieval.
    Supports LinkedIn OAuth 2.0 flow and Profile API endpoints.
    """
    
    def __init__(self):
        self.client_id = getattr(settings, 'linkedin_client_id', None)
        self.client_secret = getattr(settings, 'linkedin_client_secret', None)
        self.redirect_uri = getattr(settings, 'linkedin_redirect_uri', 'http://localhost:8000/api/v1/linkedin/callback')
        
        # LinkedIn API endpoints
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.profile_url = "https://api.linkedin.com/v2/people/~"
        self.profile_fields = "id,localizedFirstName,localizedLastName,localizedHeadline,vanityName,profilePicture(displayImage~:playableStreams)"
        
        # API rate limiting
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = datetime.now()
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL for user consent.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Authorization URL for LinkedIn OAuth flow
        """
        if not self.client_id:
            raise ValueError("LinkedIn client ID not configured")
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state or 'default_state',
            'scope': 'r_liteprofile r_emailaddress'  # Basic profile and email permissions
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated LinkedIn authorization URL for client_id: {self.client_id}")
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from LinkedIn callback
            
        Returns:
            Dictionary containing access token and metadata
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("LinkedIn credentials not configured")
        
        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(
                self.token_url,
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()
            
            token_info = response.json()
            logger.info("Successfully exchanged authorization code for access token")
            return {
                'access_token': token_info.get('access_token'),
                'expires_in': token_info.get('expires_in'),
                'token_type': token_info.get('token_type', 'Bearer'),
                'expires_at': datetime.now() + timedelta(seconds=token_info.get('expires_in', 3600))
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging authorization code: {str(e)}")
            raise Exception(f"LinkedIn token exchange failed: {str(e)}")
    
    def fetch_profile(self, access_token: str) -> Dict:
        """
        Fetch LinkedIn profile data using access token.
        
        Args:
            access_token: Valid LinkedIn access token
            
        Returns:
            Dictionary containing profile data
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Fetch basic profile
            profile_url = f"{self.profile_url}?projection=({self.profile_fields})"
            response = requests.get(profile_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            profile_data = response.json()
            
            # Fetch email separately (requires different endpoint)
            email_data = self._fetch_email(access_token)
            
            # Parse and format profile data
            formatted_profile = self._parse_profile_data(profile_data, email_data)
            
            logger.info(f"Successfully fetched LinkedIn profile for user: {formatted_profile.get('name', 'Unknown')}")
            return formatted_profile
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LinkedIn profile: {str(e)}")
            raise Exception(f"LinkedIn profile fetch failed: {str(e)}")
    
    def _fetch_email(self, access_token: str) -> Dict:
        """Fetch user email from LinkedIn email endpoint"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
            
            response = requests.get(email_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.warning(f"Could not fetch email from LinkedIn: {str(e)}")
            return {}
    
    def _parse_profile_data(self, profile_data: Dict, email_data: Dict) -> Dict:
        """
        Parse raw LinkedIn API response into standardized format.
        
        Args:
            profile_data: Raw profile data from LinkedIn API
            email_data: Raw email data from LinkedIn API
            
        Returns:
            Formatted profile dictionary
        """
        try:
            # Extract email
            email = None
            if email_data.get('elements'):
                email_element = email_data['elements'][0]
                email = email_element.get('handle~', {}).get('emailAddress')
            
            # Extract profile picture
            profile_picture_url = None
            if profile_data.get('profilePicture'):
                display_image = profile_data['profilePicture'].get('displayImage~')
                if display_image and display_image.get('elements'):
                    # Get the largest available image
                    images = display_image['elements']
                    if images:
                        profile_picture_url = images[-1].get('identifiers', [{}])[0].get('identifier')
            
            # Create LinkedIn profile URL
            vanity_name = profile_data.get('vanityName')
            linkedin_url = f"https://www.linkedin.com/in/{vanity_name}/" if vanity_name else None
            
            formatted_profile = {
                'linkedin_id': profile_data.get('id'),
                'name': f"{profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}".strip(),
                'email': email,
                'headline': profile_data.get('localizedHeadline', ''),
                'linkedin_url': linkedin_url,
                'profile_picture_url': profile_picture_url,
                'vanity_name': vanity_name,
                'raw_data': profile_data,
                'fetched_at': datetime.now().isoformat()
            }
            
            return formatted_profile
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn profile data: {str(e)}")
            raise Exception(f"Profile data parsing failed: {str(e)}")
    
    def create_or_update_user_from_linkedin(self, db: Session, profile_data: Dict, user_id: Optional[int] = None) -> User:
        """
        Create new user or update existing user with LinkedIn profile data.
        
        Args:
            db: Database session
            profile_data: Formatted LinkedIn profile data
            user_id: Optional existing user ID to update
            
        Returns:
            User object (created or updated)
        """
        try:
            if user_id:
                # Update existing user
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise ValueError(f"User with ID {user_id} not found")
                
                # Update with LinkedIn data
                user.linkedin_url = profile_data.get('linkedin_url')
                user.linkedin_id = profile_data.get('linkedin_id')
                if not user.name and profile_data.get('name'):
                    user.name = profile_data['name']
                if not user.email and profile_data.get('email'):
                    user.email = profile_data['email']
                if not user.bio and profile_data.get('headline'):
                    user.bio = profile_data['headline']
                
                logger.info(f"Updated existing user {user_id} with LinkedIn data")
                
            else:
                # Create new user from LinkedIn data
                user = User(
                    name=profile_data.get('name', 'LinkedIn User'),
                    email=profile_data.get('email'),
                    bio=profile_data.get('headline', ''),
                    linkedin_url=profile_data.get('linkedin_url'),
                    linkedin_id=profile_data.get('linkedin_id')
                )
                
                db.add(user)
                db.flush()  # Get the user ID
                logger.info(f"Created new user from LinkedIn profile: {user.name}")
            
            # Extract interests and goals from headline (basic NLP)
            if profile_data.get('headline'):
                self._extract_interests_from_headline(db, user, profile_data['headline'])
            
            db.commit()
            return user
            
        except Exception as e:
            logger.error(f"Error creating/updating user from LinkedIn: {str(e)}")
            db.rollback()
            raise
    
    def _extract_interests_from_headline(self, db: Session, user: User, headline: str):
        """
        Extract potential interests and goals from LinkedIn headline using basic NLP.
        This is a simplified implementation - you could enhance with more sophisticated NLP.
        """
        try:
            headline_lower = headline.lower()
            
            # Common tech/business keywords that might indicate interests
            tech_keywords = ['python', 'javascript', 'react', 'ai', 'machine learning', 'data science', 
                           'cloud', 'aws', 'azure', 'docker', 'kubernetes', 'blockchain']
            
            business_keywords = ['marketing', 'sales', 'finance', 'hr', 'product management', 
                               'strategy', 'consulting', 'leadership', 'entrepreneurship']
            
            # Extract interests
            found_interests = []
            for keyword in tech_keywords + business_keywords:
                if keyword in headline_lower:
                    found_interests.append(keyword.title())
            
            # Add interests to user (avoid duplicates)
            existing_interests = {interest.interest.lower() for interest in user.interests}
            for interest in found_interests[:5]:  # Limit to 5 interests
                if interest.lower() not in existing_interests:
                    db_interest = UserInterest(user_id=user.id, interest=interest)
                    db.add(db_interest)
            
            logger.info(f"Extracted {len(found_interests)} interests from LinkedIn headline")
            
        except Exception as e:
            logger.warning(f"Could not extract interests from headline: {str(e)}")
    
    def fetch_connections(self, access_token: str) -> List[Dict]:
        """
        Fetch LinkedIn connections (if user has granted permission).
        Note: LinkedIn has restricted connections API access for most applications.
        
        Args:
            access_token: Valid LinkedIn access token
            
        Returns:
            List of connection profiles
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Note: This endpoint may require special permission from LinkedIn
            connections_url = "https://api.linkedin.com/v2/connections?q=viewer&projection=(elements*(to~))"
            
            response = requests.get(connections_url, headers=headers, timeout=30)
            
            if response.status_code == 403:
                logger.warning("LinkedIn connections API access not permitted for this application")
                return []
            
            response.raise_for_status()
            connections_data = response.json()
            
            # Parse connections
            connections = []
            for element in connections_data.get('elements', []):
                connection = element.get('to~', {})
                if connection:
                    connections.append({
                        'linkedin_id': connection.get('id'),
                        'name': f"{connection.get('localizedFirstName', '')} {connection.get('localizedLastName', '')}".strip(),
                        'headline': connection.get('localizedHeadline', ''),
                        'profile_url': f"https://www.linkedin.com/in/{connection.get('vanityName', '')}/" if connection.get('vanityName') else None
                    })
            
            logger.info(f"Successfully fetched {len(connections)} LinkedIn connections")
            return connections
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LinkedIn connections: {str(e)}")
            return []
    
    def validate_token(self, access_token: str) -> bool:
        """
        Validate LinkedIn access token by making a test API call.
        
        Args:
            access_token: LinkedIn access token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(self.profile_url, headers=headers, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False

