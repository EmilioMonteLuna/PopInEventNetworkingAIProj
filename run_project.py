"""
Quick Setup and Run Script for Event Networking AI System
Automated setup, database initialization, and server startup
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Error in {description}: {result.stderr}")
            return False
        logger.info(f"✅ {description} completed successfully")
        return True
    except Exception as e:
        logger.error(f"Exception in {description}: {e}")
        return False


def setup_project():
    """Complete project setup"""
    logger.info("🚀 Starting Event Networking AI System Setup")

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher required")
        return False

    logger.info(f"✅ Python version: {sys.version}")

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False

    # Initialize database and create sample data
    logger.info("Initializing database and creating sample data...")
    try:
        from database.connection import init_database
        from database.sample_data import create_sample_data

        # Initialize database
        init_database()
        logger.info("✅ Database initialized")

        # Create sample data
        stats = create_sample_data(force_recreate=True)
        logger.info(f"✅ Sample data created: {stats}")

    except Exception as e:
        logger.error(f"Database setup error: {e}")
        return False

    # Run tests
    logger.info("Running system tests...")
    if not run_command("python -m pytest tests/test_system.py -v", "Running tests"):
        logger.warning("Some tests failed, but continuing with startup")

    logger.info("🎉 Setup completed successfully!")
    return True


def start_server():
    """Start the FastAPI server"""
    logger.info("🌐 Starting Event Networking AI Server...")
    logger.info("Server will be available at: http://localhost:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("Press Ctrl+C to stop the server")

    try:
        os.system("python main.py")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")


def display_system_info():
    """Display system information and features"""
    print("\n" + "=" * 60)
    print("   SYSTEM READY - KEY INFORMATION")
    print("=" * 60)
    print("🎯 Project: Event Networking AI System")
    print("🔗 Server URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("🧪 Test Endpoint: http://localhost:8000/api/v1/health")
    print("\n🚀 Key Features Available:")
    print("   • AI-powered networking recommendations")
    print("   • Network clustering and community detection")
    print("   • Event and user management")
    print("   • Analytics and visualization data export")
    print("   • Complete REST API for integration")
    print("\n📊 Sample Data Loaded:")
    print("   • 6 diverse user profiles")
    print("   • AI Conference 2025 with attendees")
    print("   • Ready for immediate testing")
    print("\n🔧 API Endpoints:")
    print("   • POST /api/v1/users - Create user profiles")
    print("   • POST /api/v1/events - Create events")
    print("   • POST /api/v1/recommendations/generate - Generate AI recommendations")
    print("   • POST /api/v1/clustering/analyze - Analyze network clusters")
    print("   • GET /api/v1/analytics/event/{id} - Get event analytics")
    print("=" * 60)


def main():
    """Main setup and run function"""
    print("=" * 60)
    print("   EVENT NETWORKING AI SYSTEM - QUICK SETUP")
    print("=" * 60)

    # Setup project
    if not setup_project():
        logger.error("Setup failed. Please check the errors above.")
        return

    # Display system information
    display_system_info()

    # Start server
    start_server()


if __name__ == "__main__":
    main()
