from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),unique=True)

