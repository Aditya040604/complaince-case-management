from app.database import engine, Base
from app.models import (
    Case,
    User,
    Permission,
    role_permissions,
    Role
)

Base.metadata.create_all(bind=engine)