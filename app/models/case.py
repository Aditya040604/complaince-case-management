from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.user import User







"""   
 "id": 1,
        "customer_name": "Aditya",
        "issue": "Suspicious transaction",
        "risk": "High",
        "status": "Open"


"""
class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    issue: Mapped[str] = mapped_column(String(255))
    risk: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
    assigned_user: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_to]
        
    )


