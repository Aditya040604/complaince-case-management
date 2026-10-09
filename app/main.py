from fastapi import FastAPI, status, HTTPException, Path, Depends
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.case import Case as CaseModel
from app.auth.routes import router as auth_router


DBSession = Annotated[Session, Depends(get_db)]

# ---- Models ----
class Case(BaseModel):
    customer_name: str
    issue: str
    risk: str

class CaseStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"

class CaseStatusUpdate(BaseModel):
    status: CaseStatus

class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    customer_name: str
    issue: str
    risk: str
    id: int
    status: CaseStatus

# --- FastAPI-----
app = FastAPI()
app.include_router(auth_router)

"""  
POST   /cases          → Create a case
GET    /cases          → Get all cases
GET    /cases/{id}     → Get one case
PATCH  /cases/{case_id}/status → Change case status
DELETE /cases/{id}     → Delete a case

"""


@app.get("/")
def read_root():
    return {"message": "Compliance management system"}

@app.get("/cases", response_model=list[CaseResponse])
def get_all_cases(db: DBSession):
    statement = select(CaseModel)
    result = db.execute(statement)
    cases = result.scalars().all()
    return cases
    

@app.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: Annotated[int, Path(gt=0)], db: DBSession) -> CaseResponse:
   
    statement = select(CaseModel).where(CaseModel.id == case_id)
    result = db.execute(statement)
    case = result.scalar_one_or_none()
    
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    return case
  


@app.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: Case, db: DBSession) -> CaseResponse:
    db_case = CaseModel(
        customer_name=case.customer_name,
        issue=case.issue,
        risk=case.risk,
        status="Open"
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)

    return db_case

@app.patch("/cases/{case_id}/status", response_model=CaseResponse, status_code=status.HTTP_200_OK)
def update_case_status(case_id: Annotated[int, Path(gt=0)], db: DBSession ,payload: CaseStatusUpdate) -> CaseResponse:
    stmt = select(CaseModel).where(CaseModel.id == case_id)
    case = db.scalars(stmt).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    try:
        case.status = payload.status.value
        db.commit()
        db.refresh(case)
    except:
        db.rollback()
        raise
    return case

