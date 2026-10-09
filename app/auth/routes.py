from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User
from app.auth.security import verify_password
from app.auth.jwt import create_access_token
from app.auth.schemas import TokenResponse, LoginRequest


DBSession = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    user = db.scalar(select(User).where(payload.user_name == User.user_name))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate":"Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
                            detail="User account is inactive")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )