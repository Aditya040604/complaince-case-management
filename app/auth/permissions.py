from typing import Annotated
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.permission import Permission
from app.models.role_permission import role_permissions


DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

def has_permission(db: Session, user: User,permission_name: str) -> bool:
    statement = (
        select(Permission.id)
        .join(
            role_permissions,
            role_permissions.c.permission_id == Permission.id
        )
        .where(
            role_permissions.c.role_id == user.role_id,
            Permission.name == permission_name
        )
    )
    return db.scalar(statement) is not None



def require_permission(permission_name: str):
    def permission_checker(
            db: DBSession,
            current_user: CurrentUser
    ):
        if not has_permission(db, current_user, permission_name):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You don't have permission to perform this action")
    return permission_checker