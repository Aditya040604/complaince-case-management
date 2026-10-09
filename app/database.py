from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+psycopg://compliance_user:6248@localhost:5432/compliance_db"

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()

    try: 
        yield db
    finally:
        db.close()



# with engine.connect() as connection:
#     result = connection.execute(text("SELECT current_database();"))
#     print(result.scalar())