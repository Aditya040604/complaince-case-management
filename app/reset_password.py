from sqlalchemy import select

from app.database import SessionLocal
from app.models.user import User
from app.auth.security import hash_password

def reset_password():
    db = SessionLocal()
    try:
        user = db.scalar(
            select(User).where(User.user_name == "admin")
        )
        if user is None:
            print("Admin user not found")
            return
        print("Admin user found")
        new_password = input("Enter new password:")
        user.password_hash = hash_password(new_password)
        db.commit()
        print("Admin password successfully changed")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    

if __name__ == "__main__":
    reset_password()
