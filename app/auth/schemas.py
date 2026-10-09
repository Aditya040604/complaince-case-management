from pydantic import BaseModel

class LoginRequest(BaseModel):
    user_name: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

"""  
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}

"""

