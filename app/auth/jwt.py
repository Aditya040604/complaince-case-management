from fastapi import HTTPException, status, Depends
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select


from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import timezone, timedelta, datetime
from app.database import get_db
from app.models.user import User

SECRET_KEY = "change-this-later"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DBSession = Annotated[Session, Depends(get_db)]
Token = Annotated[str, Depends(oauth2_scheme)]



""" 
1. get token bearer from token url /auth/login
2. get dbsession from database file
3. pass these to as params to our func get current user
4. create an exception which can be used to raise if token is invalid
4. decode the token bearer inside the try block to catch the error
5. extract sub which is id from decoded token
6. if the id is not an instance of str or not a digit then raise the exception
7. After that check if user exists
8. if not raise the same exception
9. if user is not active then raise 403
10. if everything is perfect then then return the user.w
"""



def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def get_current_user(token: Token, db: DBSession) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Couldn't validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                          )
    
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if not isinstance(user_id, str) or not user_id.isdigit():
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User accont is inactive",)
    return user
