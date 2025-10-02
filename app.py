from app import create_app
from app.database import init_database, check_database_exists
import os

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Initialize database if it doesn't exist
with app.app_context():
    if not check_database_exists():
        print("Database not found. Initializing...")
        init_database()
        print("Database initialized successfully!")

if __name__ == '__main__':
    app.run(debug=True)