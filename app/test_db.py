from app.database import SessionLocal
from sqlalchemy import select
from app.models.case import Case

db = SessionLocal()



case = Case(
    customer_name= "Aditya Gurram",
    issue= "Suspcious Transaction",
    risk="High",
    status="Open"

)

db.add(case)
db.commit()



statement = select(Case)
result = db.execute(statement)

cases = result.scalars().all()

for case in cases:
    print(case.id)
    print(case.customer_name)
    print(case.issue)
    print(case.status)
    print(case.risk)


# print(db)
db.close()

#TRUNCATE TABLE cases RESTART IDENTITY; --> TO RESET THE ID TO START FROM 1