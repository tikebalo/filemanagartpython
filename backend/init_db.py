"""
Initialize database and create admin user
"""
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.utils.security import hash_password
from app.config import settings

def init_database():
    """Create tables and admin user"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")

    # Create admin user
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("ℹ️  Admin user already exists")
        else:
            admin = User(
                username="admin",
                password_hash=hash_password("admin"),
                role="admin",
                quota=0  # Unlimited for admin
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created")
            print("   Username: admin")
            print("   Password: admin")
            print("   ⚠️  Please change the password after first login!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
