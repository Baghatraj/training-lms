from app.auth.password import hash_password
from app.database import SessionLocal
from app.models.user import User, UserRole


def create_admin():
    db = SessionLocal()

    try:
        email = "admin@example.com"

        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            print("Admin already exists.")
            return

        admin = User(
            name="System Admin",
            email=email,
            password_hash=hash_password("AdminPassword123!"),
            role=UserRole.ADMIN,
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()