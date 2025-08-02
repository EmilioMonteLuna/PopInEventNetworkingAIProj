#!/usr/bin/env python3
"""
Quick visualization test script to generate and display your Plotly charts
Run this to see your visualizations in action!
"""

import requests
import json
import plotly.graph_objects as go
import plotly.offline as pyo
from datetime import datetime
import webbrowser
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "visualizations"

def ensure_server_running():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running!")
            return True
    except:
        print("❌ API Server not running. Please start it with: python main.py")
        return False

def create_sample_data():
    """Create sample data for visualization"""
    print("📊 Creating sample data...")

    # Sample users
    users = [
        {
            "name": "Alice Johnson",
            "email": "alice@techcorp.com",
            "job_title": "ML Engineer",
            "company": "TechCorp",
            "industry": "Technology",
            "bio": "AI expert focused on healthcare applications",
            "experience_years": 5,
            "interests": ["Machine Learning", "Healthcare AI", "Python"],
            "goals": ["Network with data scientists", "Learn new algorithms"]
        },
        {
            "name": "Bob Smith",
            "email": "bob@dataflow.com",
            "job_title": "Data Scientist",
            "company": "DataFlow",
            "industry": "Technology",
            "bio": "Specializing in predictive analytics and visualization",
            "experience_years": 7,
            "interests": ["Data Science", "Machine Learning", "Visualization"],
            "goals": ["Share knowledge", "Find collaborators"]
        },
        {
            "name": "Carol Marketing",
            "email": "carol@brandco.com",
            "job_title": "Marketing Manager",
            "company": "BrandCo",
            "industry": "Marketing",
            "bio": "Growth marketing and customer analytics expert",
            "experience_years": 4,
            "interests": ["Marketing Analytics", "Customer Growth", "Digital Marketing"],
            "goals": ["Learn about AI tools", "Network with tech people"]
        }
    ]

    # Create users
    user_ids = []
    for user in users:
        try:
            response = requests.post(f"{API_BASE_URL}/users", json=user)
            if response.status_code == 201:
                user_ids.append(response.json()["id"])
                print(f"   ✅ Created user: {user['name']}")
        except Exception as e:
            print(f"   ⚠️ Error creating user {user['name']}: {e}")

    # Create event
    event_data = {
        "name": "AI & Data Science Networking Event",
        "description": "Connect with professionals in AI, data science, and related fields",
        "date": "2025-08-15T18:00:00",
        "location": "Toronto Convention Center",
        "event_type": "networking"
    }

    try:
        response = requests.post(f"{API_BASE_URL}/events", json=event_data)
        if response.status_code == 201:
            event_id = response.json()["id"]
            print(f"   ✅ Created event: {event_data['name']}")

            # Register users for event
            for user_id in user_ids:
                try:
                    requests.post(f"{API_BASE_URL}/events/{event_id}/register/{user_id}")
                    print(f"   ✅ Registered user {user_id} for event")
                except:
                    pass

            return event_id
    except Exception as e:
        print(f"   ⚠️ Error creating event: {e}")

    return None

def generate_cluster_visualization(event_id):
    """Generate and display the network cluster map"""
    print("🎨 Generating cluster visualization...")

    try:
        # Get the Plotly visualization data
        response = requests.get(f"{API_BASE_URL}/visualization/cluster-map?event_id={event_id}")

        if response.status_code == 200:
            fig_data = response.json()

            # Create Plotly figure
            fig = go.Figure(data=fig_data['data'], layout=fig_data['layout'])

            # Enhance the layout
            fig.update_layout(
                title="🤖 AI-Powered Networking Cluster Map",
                title_x=0.5,
                font=dict(size=14),
                plot_bgcolor='white',
                paper_bgcolor='white',
                width=1000,
                height=700
            )

            # Save and open
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            output_file = f"{OUTPUT_DIR}/cluster_map.html"
            pyo.plot(fig, filename=output_file, auto_open=True)
            print(f"   ✅ Cluster map saved to: {output_file}")

            return True

    except Exception as e:
        print(f"   ❌ Error generating cluster visualization: {e}")
        return False

def generate_recommendations_demo(event_id):
    """Show AI recommendations in action"""
    print("🧠 Generating AI recommendations...")

    try:
        # Get event attendees first
        response = requests.get(f"{API_BASE_URL}/events/{event_id}")
        if response.status_code == 200:
            event_data = response.json()
            print(f"   📊 Event: {event_data['name']}")

        # Get recommendations for first user
        response = requests.post(f"{API_BASE_URL}/recommendations/generate",
                               json={"event_id": event_id, "max_recommendations": 5})

        if response.status_code == 200:
            recommendations = response.json()
            print(f"   ✅ Generated {recommendations['total_generated']} AI recommendations")

            # Display sample recommendations
            for rec in recommendations['recommendations'][:3]:
                print(f"   🤝 {rec['user_name']} → {rec['recommended_user_name']}")
                print(f"      💯 Similarity: {rec['similarity_score']:.2f}")
                print(f"      💡 Reason: {rec['reason'][:80]}...")
                print()

            return True

    except Exception as e:
        print(f"   ❌ Error generating recommendations: {e}")
        return False

def generate_analytics_visualization(event_id):
    """Generate analytics charts"""
    print("📈 Generating analytics visualization...")

    try:
        # Get event analytics
        response = requests.get(f"{API_BASE_URL}/analytics/event/{event_id}")

        if response.status_code == 200:
            analytics = response.json()

            # Create analytics dashboard
            fig = go.Figure()

            # Add metrics as bar chart
            metrics = ['Total Users', 'Total Recommendations', 'High Confidence Recs']
            values = [
                analytics['total_registered'],
                analytics['total_recommendations'],
                analytics['high_confidence_recommendations']
            ]

            fig.add_trace(go.Bar(
                x=metrics,
                y=values,
                marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
                text=values,
                textposition='auto'
            ))

            fig.update_layout(
                title="📊 Event Analytics Dashboard",
                title_x=0.5,
                xaxis_title="Metrics",
                yaxis_title="Count",
                font=dict(size=14),
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            # Save analytics
            output_file = f"{OUTPUT_DIR}/analytics_dashboard.html"
            pyo.plot(fig, filename=output_file, auto_open=True)
            print(f"   ✅ Analytics dashboard saved to: {output_file}")

            return True

    except Exception as e:
        print(f"   ❌ Error generating analytics: {e}")
        return False

def main():
    """Main visualization demo"""
    print("🎨 AI Event Networking - Visualization Demo")
    print("=" * 50)

    # Check server
    if not ensure_server_running():
        return

    # Create sample data
    event_id = create_sample_data()
    if not event_id:
        print("❌ Failed to create sample data")
        return

    print(f"\n🎯 Using Event ID: {event_id}")
    print("=" * 50)

    # Generate visualizations
    success_count = 0

    if generate_cluster_visualization(event_id):
        success_count += 1

    if generate_recommendations_demo(event_id):
        success_count += 1

    if generate_analytics_visualization(event_id):
        success_count += 1

    print("\n🎉 Visualization Demo Complete!")
    print("=" * 50)
    print(f"✅ Successfully generated {success_count}/3 visualizations")
    print(f"📁 Check the '{OUTPUT_DIR}' folder for HTML files")
    print("🌐 Files should open automatically in your browser")

    # Open folder
    if os.path.exists(OUTPUT_DIR):
        os.startfile(OUTPUT_DIR)  # Windows
        print(f"📂 Opened '{OUTPUT_DIR}' folder")

if __name__ == "__main__":
    main()
