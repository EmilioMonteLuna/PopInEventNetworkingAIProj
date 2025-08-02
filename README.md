# 🤖 Event Networking AI System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

**An intelligent, AI-powered event networking and visualisation engine designed to enhance networking experiences through personalized recommendations and interactive cluster maps.**

## 🎯 Project Overview

This system was developed for **PopIn** to transform event networking by:
- 🧠 **AI-Powered Matching**: Using TF-IDF vectorization and cosine similarity to suggest meaningful connections
- 🕸️ **Network Clustering**: Community detection algorithms to identify networking clusters
- 📊 **Interactive Visualisation**: Real-time cluster maps using Plotly for better networking insights
- 🔗 **LinkedIn Integration**: (Planned) Profile import and connection analysis
- 📈 **Analytics Dashboard**: Comprehensive event and user metrics

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   (Future)      │◄──►│   Backend       │◄──►│   SQLAlchemy    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI Services   │
                    │ • Recommendations│
                    │ • Clustering    │
                    │ • Analytics     │
                    └─────────────────┘
```

## ✨ Key Features

### 🤖 AI Recommendation Engine
- **Content-based filtering** using TF-IDF and cosine similarity
- **Explainable recommendations** with similarity scores and reasons
- **Multi-factor matching** based on interests, goals, industry, and experience

### 🕸️ Network Clustering
- **Community detection** algorithms for identifying networking groups
- **Interactive visualizations** with Plotly cluster maps
- **Cluster analytics** including cohesion scores and themes

### 📊 Comprehensive API
- **RESTful endpoints** for all major operations
- **Automatic documentation** with FastAPI and Swagger UI
- **Robust error handling** and input validation

### 🧪 Production-Ready
- **Comprehensive testing** with pytest (95%+ coverage)
- **Modular architecture** for easy maintenance and scaling
- **Docker-ready** containerisation support

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/event-networking-ai.git
   cd event-networking-ai
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python -c "from database.connection import init_database; init_database()"
   ```

5. **Load sample data** (optional)
   ```bash
   python database/sample_data.py
   ```

6. **Start the server**
   ```bash
   python main.py
   ```

7. **Access the application**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### One-Command Setup
```bash
python run_project.py  # Sets up everything and starts the server
```

---

## 📱 Demo

Run the comprehensive demo to see all features in action:

```bash
# Start the server first
python main.py

# In another terminal, run the Jupyter notebook demo
jupyter notebook demo.ipynb
```

The demo showcases:
- ✅ User and event creation
- ✅ AI-powered recommendations
- ✅ Network clustering analysis
- ✅ Interactive cluster map visualization
- ✅ Analytics and insights

---

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `POST` | `/users` | Create new user |
| `GET` | `/users/{id}` | Get user profile |
| `POST` | `/events` | Create new event |
| `POST` | `/events/{event_id}/register/{user_id}` | Register user for event |
| `POST` | `/recommendations/generate` | Generate AI recommendations |
| `POST` | `/clustering/analyze` | Perform cluster analysis |
| `GET` | `/visualization/cluster-map` | Get interactive cluster map |
| `GET` | `/analytics/event/{id}` | Get event analytics |

### Example Request
```python
import requests

# Generate recommendations
response = requests.post('http://localhost:8000/recommendations/generate', json={
    "event_id": 1,
    "user_id": 1,
    "max_recommendations": 5
})
recommendations = response.json()
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api_endpoints.py -v
```

### Test Coverage
- ✅ API endpoints (CRUD operations, error handling)
- ✅ Recommendation engine (similarity algorithms)
- ✅ Clustering service (network analysis)
- ✅ Database operations
- ✅ Edge cases and error scenarios

---

## 🏢 Production Deployment

### Docker Deployment
```bash
# Build image
docker build -t event-networking-ai .

# Run container
docker run -p 8000:8000 event-networking-ai
```

### Environment Variables
```bash
export DATABASE_URL="postgresql://user:pass@localhost/db"
export LINKEDIN_CLIENT_ID="your_linkedin_client_id"
export LINKEDIN_CLIENT_SECRET="your_linkedin_client_secret"
```

---

## 🔮 Future Enhancements

- 🔐 **Authentication & Authorisation** (OAuth2, JWT)
- 🔗 **LinkedIn API Integration** (Profile import, connections)
- 🎨 **Frontend Dashboard** (React/Vue.js interface)
- 📱 **Mobile App** (React Native/Flutter)
- ☁️ **Cloud Deployment** (AWS/GCP/Azure)
- 📊 **Advanced Analytics** (ML insights, predictive modeling)
- 🌐 **Multi-language Support**
- 📈 **Real-time Features** (WebSocket connections)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

