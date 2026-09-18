from fastapi import FastAPI, status, HTTPException, Path
from pydantic import BaseModel
from enum import Enum
from typing import Annotated


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
    customer_name: str
    issue: str
    risk: str
    id: int
    status: CaseStatus





# --- FastAPI-----
app = FastAPI()

"""  
POST   /cases          → Create a case
GET    /cases          → Get all cases
GET    /cases/{id}     → Get one case
PATCH  /cases/{case_id}/status → Change case status
DELETE /cases/{id}     → Delete a case

"""

cases = [
    {
        "id": 1,
        "customer_name": "Aditya",
        "issue": "Suspicious transaction",
        "risk": "High",
        "status": "Open"

    }

]


@app.get("/")
def read_root():
    return {"message": "Compliance management system"}

@app.get("/cases")
def get_all_cases():
    return cases

@app.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: Annotated[int, Path(gt=0)]) -> CaseResponse:
   
    for case in cases:
        if case.get("id") == case_id:
            return case
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")
   


@app.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case: Case) -> CaseResponse:
    id = max(case["id"] for case in cases) + 1
    status = "Open"
    data = {**case.model_dump(), "id": id, "status": status}
    cases.append(data)
    return data

@app.patch("/cases/{case_id}/status", response_model=CaseResponse, status_code=status.HTTP_200_OK)
def update_status(case_id: Annotated[int, Path(gt=0)], updated_status: CaseStatusUpdate) -> CaseResponse:
    for case in cases:
        if case.get('id') == case_id:
            data = updated_status.model_dump()
            case.update(**data)
            return case
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case with ID {case_id} not found.")


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}