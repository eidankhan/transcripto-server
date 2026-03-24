import asyncio
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password # Assuming this is your helper name
from sqlalchemy.future import select

async def create_initial_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_email = "admin@transcripto.dev"
        result = db.execute(select(User).filter(User.email == admin_email))
        existing_admin = result.scalars().first()

        if existing_admin:
            print(f"Admin with email {admin_email} already exists.")
            return

        # Create new admin
        new_admin = User(
            name="Eidan Khan",
            email=admin_email,
            password_hash=hash_password("admin123"), # Generates the bcrypt hash
            is_verified=True,
            role=UserRole.ADMIN
        )

        db.add(new_admin)
        db.commit()
        print(f"Successfully created ADMIN user: {admin_email}")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_initial_admin())