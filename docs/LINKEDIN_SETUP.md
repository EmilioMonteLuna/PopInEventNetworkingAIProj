# LinkedIn API Integration Setup Guide

This guide will help you set up LinkedIn API integration for the Event Networking AI System.

## 📋 Prerequisites

1. **LinkedIn Developer Account**: You need a LinkedIn developer account
2. **LinkedIn App**: Create a LinkedIn application for OAuth integration
3. **Valid Domain**: LinkedIn requires a valid redirect URI (can be localhost for development)

## 🚀 Step-by-Step Setup

### 1. Create LinkedIn Developer Application

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Sign in with your LinkedIn account
3. Click **"Create App"**
4. Fill in the application details:
   - **App name**: `Event Networking AI`
   - **LinkedIn Page**: Your company/personal LinkedIn page
   - **Privacy policy URL**: Your privacy policy URL
   - **App logo**: Upload a logo (optional)
5. Click **"Create app"**

### 2. Configure OAuth Settings

1. In your LinkedIn app dashboard, go to **"Auth"** tab
2. Add **Authorized redirect URLs**:
   ```
   http://localhost:8000/api/v1/linkedin/callback
   ```
   (Add your production domain when deploying)

3. Under **"OAuth 2.0 scopes"**, request access to:
   - `r_liteprofile` - Basic profile information
   - `r_emailaddress` - Email address

### 3. Get API Credentials

1. In the **"Auth"** tab, copy:
   - **Client ID**
   - **Client Secret**

### 4. Configure Environment Variables

Create a `.env` file in your project root:

```bash
# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/linkedin/callback
```

Or set environment variables directly:

```bash
export LINKEDIN_CLIENT_ID="your_client_id_here"
export LINKEDIN_CLIENT_SECRET="your_client_secret_here"
export LINKEDIN_REDIRECT_URI="http://localhost:8000/api/v1/linkedin/callback"
```

### 5. Update Database Schema

The LinkedIn integration requires a new field in the User model. If you have existing data, you'll need to migrate:

```bash
# For new installations, just run:
python -c "from database.connection import init_database; init_database()"

# For existing databases with data, you may need to add the column manually:
# ALTER TABLE users ADD COLUMN linkedin_id VARCHAR(100) UNIQUE;
```

## 🔄 OAuth Flow

### 1. Initiate Authentication

```bash
GET /api/v1/linkedin/auth
```

Response:
```json
{
  "authorization_url": "https://www.linkedin.com/oauth/v2/authorization?...",
  "state": "security_token",
  "instructions": "Visit the authorization URL to grant LinkedIn permissions"
}
```

### 2. Handle Callback

After user grants permissions, LinkedIn redirects with an authorization code:

```bash
POST /api/v1/linkedin/callback
Content-Type: application/json

{
  "authorization_code": "received_from_linkedin",
  "state": "security_token",
  "user_id": 123  // Optional: to update existing user
}
```

### 3. Import LinkedIn Data for Existing User

```bash
POST /api/v1/users/{user_id}/linkedin-import
Content-Type: application/json

{
  "authorization_code": "received_from_linkedin"
}
```

## 📊 What Data is Imported

The LinkedIn integration automatically imports:

- **Basic Profile**: Name, headline, profile picture
- **Contact Info**: Email address (if permitted)
- **Professional Info**: Current position, company
- **Interests**: Extracted from headline using keyword matching
- **LinkedIn URL**: Direct link to LinkedIn profile

## 🧪 Testing the Integration

### 1. Start the Server

```bash
python main.py
```

### 2. Test Authentication Flow

```bash
# Get authorization URL
curl http://localhost:8000/api/v1/linkedin/auth

# Visit the returned URL in your browser
# Grant permissions on LinkedIn
# Copy the authorization code from the callback URL
```

### 3. Complete the Flow

```bash
# Use the authorization code
curl -X POST http://localhost:8000/api/v1/linkedin/callback \
  -H "Content-Type: application/json" \
  -d '{"authorization_code": "YOUR_CODE_HERE"}'
```

## 🔒 Security Considerations

1. **Store Credentials Securely**: Never commit API keys to version control
2. **Use HTTPS in Production**: LinkedIn requires HTTPS for production apps
3. **Validate State Parameter**: Always validate the state parameter to prevent CSRF
4. **Token Management**: Access tokens expire - implement refresh logic if needed
5. **Rate Limiting**: LinkedIn has rate limits - implement proper error handling

## 🚨 Troubleshooting

### Common Issues

1. **"LinkedIn integration not configured"**
   - Check that `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` are set
   - Restart the server after setting environment variables

2. **"Invalid redirect URI"**
   - Ensure the redirect URI in your LinkedIn app matches exactly
   - Check for trailing slashes and protocol (http vs https)

3. **"Insufficient permissions"**
   - Ensure your LinkedIn app has requested the correct scopes
   - Some features may require LinkedIn partner status

4. **"Token exchange failed"**
   - Check that your client secret is correct
   - Ensure the authorization code hasn't expired (10 minutes)

### Debug Mode

Enable debug logging in `config/settings.py`:

```python
debug: bool = True
log_level: str = "DEBUG"
```

## 🎯 Production Deployment

### 1. Update Redirect URI

Update your LinkedIn app's authorized redirect URLs to include your production domain:

```
https://your-domain.com/api/v1/linkedin/callback
```

### 2. Environment Variables

Set production environment variables:

```bash
LINKEDIN_CLIENT_ID=your_production_client_id
LINKEDIN_CLIENT_SECRET=your_production_client_secret
LINKEDIN_REDIRECT_URI=https://your-domain.com/api/v1/linkedin/callback
ENVIRONMENT=production
```

### 3. HTTPS Required

LinkedIn requires HTTPS for production applications. Ensure your deployment uses SSL certificates.

## 📈 Usage Analytics

The system automatically tracks:
- LinkedIn profile imports
- User profile completeness improvements
- Interest/skill extraction success rates

Check the logs for detailed information about LinkedIn integration usage.

## 🆘 Support

If you encounter issues:

1. Check the [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
2. Review the application logs for detailed error messages
3. Ensure your LinkedIn app has the necessary permissions
4. Contact LinkedIn Developer Support for API-specific issues

## 🔄 Updates and Maintenance

- **Monitor API Changes**: LinkedIn occasionally updates their API
- **Refresh Tokens**: Implement token refresh if using long-lived integrations
- **Rate Limit Monitoring**: Track your API usage against LinkedIn's limits
- **User Consent**: Ensure compliance with data privacy regulations

---

**Note**: This integration enhances your event networking system by automatically importing professional profiles, but the system remains fully functional even without LinkedIn integration using manually entered profile data.