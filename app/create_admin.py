from sqlalchemy import select

from app.database import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.auth.security import hash_password

db = SessionLocal()

try:

    role = db.scalar(
        select(Role).where(Role.name == "Admin")
    )
    if role is None:
        raise RuntimeError("Admin role does not exist..")
    existing_user = db.scalar(
        select(User).where(User.user_name == "admin")
    )
    if existing_user is None:
        user = User(
            user_name = "admin",
            email = "admin@example.com",
            password_hash=hash_password("Admin@123"),
            role_id = role.id,
        )
        db.add(user)
        db.commit()
        print("Admin user created.")

    else:
        print("Admin user already exists.")



finally:
    db.close()