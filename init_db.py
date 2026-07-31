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
    print("📋 Default Users:")
    print("   Admin: admin / admin123")
    print("   Staff: sarah / staff123")
    print("   Staff: mike / staff123")
    print("   Staff: emma / staff123")
    print("   Staff: alex / staff123")
    print()
    print("🚀 Start the server: cd backend && python3 run.py")