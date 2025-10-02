#!/usr/bin/env python3
"""
Database initialization script for the Compliance Document Management System.
Run this script to set up the database with required tables and sample data.
"""

import os
import sys
from app import create_app
from app.database import init_database, check_database_exists, create_sample_data

def main():
    """Main function to initialize the database."""
    print("Initializing Compliance Document Management System Database...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Check if database already exists
            if check_database_exists():
                response = input("Database already exists. Do you want to recreate it? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("Database initialization cancelled.")
                    return
                
                # Reset database if user confirms
                from app.database import reset_database
                reset_database()
            else:
                # Initialize new database
                init_database()
            
            # Ask if user wants sample data
            response = input("Do you want to create sample users for testing? (Y/n): ")
            if response.lower() not in ['n', 'no']:
                create_sample_data()
            
            print("\n✅ Database initialization completed successfully!")
            print("\nSample users (if created):")
            print("  Admin: admin@compliance.com / admin123")
            print("  User:  user@compliance.com / user123")
            print("\nYou can now run the application with: python app.py")
            
        except Exception as e:
            print(f"\n❌ Error during database initialization: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()