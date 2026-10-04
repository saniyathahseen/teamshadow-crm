"""
Database initialization script.
Run this to create/reset the database with default data.
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import init_db

if __name__ == "__main__":
    print("=" * 50)
    print("Team Shadow Weddings CRM - Database Initialization")
    print("=" * 50)
    
    # Remove existing database
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'teamshadow.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️  Removed existing database: {db_path}")
    
    # Initialize
    init_db()
    print("✅ Database created successfully!")
    print()
    print("📋 Environment-based setup is required for admin/staff accounts.")
    print("Set TEAMSHADOW_ADMIN_USERNAME, TEAMSHADOW_ADMIN_PASSWORD, and TEAMSHADOW_STAFF_PASSWORD before starting the app.")
    print()
    print("🚀 Start the server: cd backend && python3 run.py")