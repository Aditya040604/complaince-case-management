from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base







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


