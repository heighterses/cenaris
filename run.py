#!/usr/bin/env python3
"""
Run script for the Compliance Document Management System.
This script starts the Flask development server.
"""

from app import create_app
from app.database import init_database, check_database_exists
import os

# Create the Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# Initialize database if it doesn't exist
with app.app_context():
    if not check_database_exists():
        print("Database not found. Initializing...")
        init_database()
        print("Database initialized successfully!")

if __name__ == '__main__':
    print("🚀 Starting Compliance Document Management System...")
    print("📊 Dashboard will be available at: http://127.0.0.1:5000")
    print("🔐 Create an account or use sample users:")
    print("   • admin@compliance.com / admin123")
    print("   • user@compliance.com / user123")
    print("\n⚠️  Note: Azure Storage is not configured. File uploads will show an error.")
    print("   To enable uploads, set AZURE_STORAGE_CONNECTION_STRING in your .env file")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )