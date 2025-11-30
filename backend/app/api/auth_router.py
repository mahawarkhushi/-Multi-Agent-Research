# app/api/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

from app.db.user import User
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

# -----------------------------
# LOGIN
# -----------------------------
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 form uses `username` → treat as email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

# -----------------------------
# REFRESH TOKEN
# -----------------------------
def get_refresh_token(authorization: str = Header(...)) -> dict:
    """
    Extracts and verifies refresh token from Authorization header.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    token = authorization[len("Bearer "):]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    return payload

@router.post("/refresh")
def refresh_token(payload: dict = Depends(get_refresh_token)):
    """
    Issue new access token using a valid refresh token.
    """
    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Issue new access token
    new_access_token = create_access_token({"sub": user_id, "role": role})
    return {"access_token": new_access_token, "token_type": "Bearer"}

# -----------------------------
# HELPER TO CREATE TEST USER
# -----------------------------
def create_test_user(
    db: Session,
    email: str,
    password: str,
    full_name: str = "Test User",
    role: str = "admin"
) -> User:
    """
    Insert a new user into DB with hashed password.
    Example:
        create_test_user(db, "john@example.com", "Test1234")
    """
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing  # User already exists

    hashed_pw = hash_password(password)
    new_user = User(
        full_name=full_name,
        email=email,
        role=role,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
