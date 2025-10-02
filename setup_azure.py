#!/usr/bin/env python3
"""
Azure Data Lake Storage Setup Script
This script helps you configure Azure ADLS credentials securely.
"""

import os
import sys

def setup_azure_credentials():
    """Interactive setup for Azure ADLS credentials."""
    print("🔧 Azure Data Lake Storage Setup")
    print("=" * 50)
    print()
    
    # Check if .env file exists
    env_file = '.env'
    env_exists = os.path.exists(env_file)
    
    if env_exists:
        print("📁 Found existing .env file")
        response = input("Do you want to update Azure credentials? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    else:
        print("📁 Creating new .env file")
    
    print()
    print("Please provide your Azure Data Lake Storage credentials:")
    print("(You can find these in your Azure Portal > Storage Account > Access Keys)")
    print()
    
    # Get connection string
    connection_string = input("🔑 Azure Storage Connection String: ").strip()
    if not connection_string:
        print("❌ Connection string is required!")
        return
    
    # Get container name
    container_name = input("📦 Container/File System Name (default: compliance-documents): ").strip()
    if not container_name:
        container_name = "compliance-documents"
    
    # Read existing .env content if it exists
    env_content = {}
    if env_exists:
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value
        except Exception as e:
            print(f"⚠️  Warning: Could not read existing .env file: {e}")
    
    # Update with new values
    env_content['AZURE_STORAGE_CONNECTION_STRING'] = connection_string
    env_content['AZURE_CONTAINER_NAME'] = container_name
    
    # Set default values if not present
    if 'FLASK_CONFIG' not in env_content:
        env_content['FLASK_CONFIG'] = 'development'
    if 'SECRET_KEY' not in env_content:
        env_content['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
    if 'DATABASE_URL' not in env_content:
        env_content['DATABASE_URL'] = 'sqlite:///compliance.db'
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write("# Flask Configuration\n")
            f.write(f"FLASK_CONFIG={env_content['FLASK_CONFIG']}\n")
            f.write(f"SECRET_KEY={env_content['SECRET_KEY']}\n")
            f.write("\n")
            f.write("# Azure Data Lake Storage Configuration\n")
            f.write(f"AZURE_STORAGE_CONNECTION_STRING={env_content['AZURE_STORAGE_CONNECTION_STRING']}\n")
            f.write(f"AZURE_CONTAINER_NAME={env_content['AZURE_CONTAINER_NAME']}\n")
            f.write("\n")
            f.write("# Database Configuration\n")
            f.write(f"DATABASE_URL={env_content['DATABASE_URL']}\n")
        
        print()
        print("✅ Azure credentials configured successfully!")
        print(f"📁 Container/File System: {container_name}")
        print()
        print("🔒 Your credentials are stored securely in .env file")
        print("⚠️  Make sure .env is in your .gitignore to keep credentials private")
        print()
        print("Next steps:")
        print("1. Install new dependencies: pip install -r requirements.txt")
        print("2. Run the application: python3 run.py")
        print("3. Test file upload functionality")
        
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return

def test_azure_connection():
    """Test Azure ADLS connection."""
    print("🧪 Testing Azure Data Lake Storage Connection")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.services.azure_storage import AzureBlobStorageService
        
        app = create_app()
        with app.app_context():
            storage_service = AzureBlobStorageService()
            
            if storage_service.is_configured():
                print("✅ Azure ADLS is properly configured!")
                print(f"📦 Container/File System: {storage_service.container_name}")
                
                # Try to list files (this will also test connection)
                result = storage_service.list_files()
                if result['success']:
                    print(f"📁 Found {result['count']} files in storage")
                    print("🎉 Connection test successful!")
                else:
                    print(f"⚠️  Warning: {result['error']}")
            else:
                print("❌ Azure ADLS is not configured")
                print("Run this script first to set up credentials")
                
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_azure_connection()
    else:
        setup_azure_credentials()

if __name__ == '__main__':
    main()