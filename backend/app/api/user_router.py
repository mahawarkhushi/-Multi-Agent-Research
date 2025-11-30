from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserRead
from app.db.user import User
from app.dependencies import get_db
import uuid
router = APIRouter(prefix="/users", tags=["Users"])

# -----------------------------
# CREATE USER
# -----------------------------
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already taken"
        )

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        role=data.role,
        hashed_password=data.password  # TODO: Hash in production
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# -----------------------------
# READ USERS with Pagination + Filtering
# -----------------------------
@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    role: str | None = None,
):
    if skip < 0 or limit <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid pagination values"
        )

    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()

# -----------------------------
# GET USER BY ID
# -----------------------------
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# -----------------------------
# DELETE USER
# -----------------------------
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}