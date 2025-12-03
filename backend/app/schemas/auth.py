from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = "User"  # default role

class UserRead(BaseModel):
    id: UUID  
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class TokenRefresh(BaseModel):
    refresh_token: str
