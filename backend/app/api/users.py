# app/api/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.user import User
from app.dependencies import get_db, require_role

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/")
def create_user(user: User, db: Session = Depends(get_db), token: str = Depends()):
    require_role(token, ["Admin"])
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/")
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), token: str = Depends()):
    require_role(token, ["Admin"])
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/filter")
def filter_users(role: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == role).all()
