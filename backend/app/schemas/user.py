from pydantic import BaseModel, EmailStr, Field
from typing import Literal
import uuid

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal["admin", "analyst", "viewer"]

class UserRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: str

    class Config:
        orm_mode = True
