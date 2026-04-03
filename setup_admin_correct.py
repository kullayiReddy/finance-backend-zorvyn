"""
Setup Admin User - Fixed Import Paths
Run this to create the first admin user
"""
import sys
import os

# Add current directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.database import SessionLocal, init_db
from src.services.user_service import UserService
from src.models.models import UserRole
from src.models.schemas import UserCreate

def setup_admin():
    """Create admin user"""
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Get session
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin = UserService.get_user_by_email(db, "admin@example.com")
        if admin:
            print("✗ Admin user already exists!")
            return
        
        # Create admin user
        admin_data = UserCreate(
            email="admin@example.com",
            password="admin123",
            full_name="Administrator",
            role="admin"
        )
        
        admin = UserService.create_user(db, admin_data)
        print("✓ Admin user created successfully!")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin123")
        print(f"  Role: admin")
        print("\n⚠️  IMPORTANT: Change the password in production!")
        
        # Create sample analyst user
        analyst_data = UserCreate(
            email="analyst@example.com",
            password="analyst123",
            full_name="Analyst User",
            role="analyst"
        )
        
        analyst = UserService.create_user(db, analyst_data)
        print("\n✓ Analyst user created!")
        print(f"  Email: analyst@example.com")
        print(f"  Password: analyst123")
        
        # Create sample viewer user
        viewer_data = UserCreate(
            email="viewer@example.com",
            password="viewer123",
            full_name="Viewer User",
            role="viewer"
        )
        
        viewer = UserService.create_user(db, viewer_data)
        print("\n✓ Viewer user created!")
        print(f"  Email: viewer@example.com")
        print(f"  Password: viewer123")
        
        print("\n" + "="*60)
        print("Setup Complete! You can now login with these credentials.")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python -m src")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Login with admin@example.com / admin123")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    setup_admin()

