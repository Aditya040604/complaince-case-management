from fastapi import FastAPI, status, HTTPException, Path, Depends
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.case import Case as CaseModel
from app.auth.routes import router as auth_router
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.role import Role
from app.auth.permissions import require_permission, has_permission
from app.services.audit_service import create_audit_log



DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# ---- Models ----
class CaseCreate(BaseModel):
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

class CaseAssignment(BaseModel):
    assigned_to: int

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

@app.get("/cases", 
         dependencies=[
             Depends(require_permission("cases:read"))
         ]
         ,response_model=list[CaseResponse])
def get_all_cases(db: DBSession):
    statement = select(CaseModel)
    result = db.execute(statement)
    cases = result.scalars().all()
    return cases
    

@app.get("/cases/{case_id}" , 
         dependencies=[
             Depends(require_permission("cases:read"))
         ], response_model=CaseResponse)
def get_case(case_id: Annotated[int, Path(gt=0)], db: DBSession) -> CaseResponse:
   
    statement = select(CaseModel).where(CaseModel.id == case_id)
    result = db.execute(statement)
    case = result.scalar_one_or_none()
    
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    return case
  


@app.post("/cases", 
          dependencies=[
              Depends(require_permission("cases:create"))
          ]
          ,response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: CaseCreate, db: DBSession, current_user: CurrentUser) -> CaseResponse:
    
    try:
        db_case = CaseModel(
        customer_name=case.customer_name,
        issue=case.issue,
        risk=case.risk,
        status="Open"
    )
        db.add(db_case)
        db.flush()
        create_audit_log(
            db, 
            action="CASE_CREATED",
            entity_type="case",
            entity_id=db_case.id,
            user_id= current_user.id,
            case_id= db_case.id)
        db.commit()
        db.refresh(db_case)
    except Exception:
        db.rollback()
        raise
    return db_case

@app.patch("/cases/{case_id}/status", response_model=CaseResponse, status_code=status.HTTP_200_OK)
def update_case_status(case_id: Annotated[int, Path(gt=0)], db: DBSession, current_user: CurrentUser,payload: CaseStatusUpdate) -> CaseResponse:
    # 1. Retrive the case
    case = db.get(CaseModel, case_id)
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
    # 2. Determine required permission
    allowed_transitions = {
        CaseStatus.OPEN: {
            CaseStatus.IN_PROGRESS,
            CaseStatus.CLOSED
        },
        CaseStatus.IN_PROGRESS: {
            CaseStatus.CLOSED
        },
        CaseStatus.CLOSED: set()
    }
    current_status = CaseStatus(case.status)
    if payload.status not in allowed_transitions[current_status]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid case status transition.")
    
    if payload.status == CaseStatus.CLOSED:
        required_permission = "cases:close"
    else:
        required_permission = "cases:update"
    # 3. Check permission
    if not has_permission(db, current_user, required_permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to perform this action.")
  
    try:
        old_status = case.status
        new_status = payload.status.value
        case.status = new_status
        
        create_audit_log(
            db,
            action="CASE_CLOSED" if payload.status.value == "Closed" else "CASE_STATUS_CHANGED",
            entity_type="case",
            case_id=case.id,
            user_id=current_user.id,
            entity_id=case.id,
            old_value=old_status,
            new_value=new_status
        )
        db.commit()
        db.refresh(case)
    except Exception:
        db.rollback()
        raise
    return case

@app.patch("/cases/{case_id}/assign", dependencies=[Depends(require_permission("cases:assign"))])
def assign_case(case_id: Annotated[int, Path(gt=0)], case_assign: CaseAssignment,db: DBSession, current_user: CurrentUser):
    case = db.get(CaseModel, case_id)
    not_found_exc = lambda detail: HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )
    bad_request_exc = lambda detail: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )
    if not case:
        raise not_found_exc("There are no cases with the provided ID.")
    analyst = db.get(User,case_assign.assigned_to)
    if not analyst:
        raise not_found_exc("Target user not found.")
    if not analyst.is_active:
        raise bad_request_exc("Target user is inactive, cannot assign case to an inactive user.")
    role= db.get(Role, analyst.role_id)

    if role is None or role.name != "Analyst":
        raise bad_request_exc("Cases can only be assigned to Analysts.")
    if case.status == "Closed":
        raise bad_request_exc("Case is already closed and cannot be assigned now.")
    if case.assigned_to == case_assign.assigned_to:
        return case
    try:
        old_assigned_id = case.assigned_to
        new_assigned_id = case_assign.assigned_to
        case.assigned_to = new_assigned_id
        # add case assignment to audit log
        create_audit_log(
            db=db,
            action=(
                "CASE_REASSIGNED" if old_assigned_id is not None else "CASE_ASSIGNED" 
                ),
            entity_type="case",
            entity_id=case.id,
            case_id=case.id,
            user_id=current_user.id,
            old_value=str(old_assigned_id),
            new_value=str(new_assigned_id)

        )

        db.commit()
        db.refresh(case)
    except Exception:
        db.rollback()
        raise
    return case
    

@app.get("/auth/me")
def read_current_user(current_user: CurrentUser):
    return {
        "id": current_user.id,
        "user_name": current_user.user_name,
        "is_active": current_user.is_active

    }