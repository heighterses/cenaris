import sqlite3
import os
from flask import current_app

def get_db_connection():
    """Get database connection with proper configuration."""
    db_path = current_app.config.get('DATABASE_URL', 'sqlite:///compliance.db').replace('sqlite:///', '')
    
    # Ensure directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                blob_name VARCHAR(255) UNIQUE NOT NULL,
                file_size INTEGER,
                content_type VARCHAR(100),
                uploaded_by INTEGER NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_is_active ON documents(is_active)')
        
        conn.commit()
        print("Database initialized successfully!")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise e
    finally:
        conn.close()

def check_database_exists():
    """Check if database file exists and has required tables."""
    db_path = current_app.config.get('DATABASE_URL', 'sqlite:///compliance.db').replace('sqlite:///', '')
    
    if not os.path.exists(db_path):
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if required tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('users', 'documents')
        """)
        
        tables = cursor.fetchall()
        conn.close()
        
        return len(tables) == 2  # Both tables should exist
        
    except sqlite3.Error:
        return False

def create_sample_data():
    """Create sample data for development/testing."""
    from app.models import User
    
    try:
        # Create a sample admin user
        admin_user = User.create_user('admin@compliance.com', 'admin123')
        if admin_user:
            print("Sample admin user created: admin@compliance.com / admin123")
        else:
            print("Admin user already exists")
            
        # Create a sample regular user
        user = User.create_user('user@compliance.com', 'user123')
        if user:
            print("Sample user created: user@compliance.com / user123")
        else:
            print("Regular user already exists")
            
    except Exception as e:
        print(f"Error creating sample data: {e}")

def reset_database():
    """Reset database by dropping and recreating all tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Drop existing tables
        cursor.execute('DROP TABLE IF EXISTS documents')
        cursor.execute('DROP TABLE IF EXISTS users')
        
        conn.commit()
        conn.close()
        
        # Reinitialize database
        init_database()
        print("Database reset successfully!")
        
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        print(f"Error resetting database: {e}")
        raise e