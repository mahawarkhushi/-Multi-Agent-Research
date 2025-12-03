from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.user import User
from app.dependencies import get_db
from app.schemas.auth import UserCreate, Token, TokenRefresh, UserRead
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

# -------------------------
# Signup (for Admin/User creation)
# -------------------------
@router.post("/signup", response_model=UserRead)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# -------------------------
# Login
# -------------------------
@router.post("/login", response_model=Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token}

# -------------------------
# Refresh Token
# -------------------------
@router.post("/refresh", response_model=Token)
def refresh_token(data: TokenRefresh):
    payload = verify_token(data.refresh_token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    access_token = create_access_token({"sub": payload["sub"], "role": payload.get("role", "User")})
    refresh_token = create_refresh_token({"sub": payload["sub"]})
    return {"access_token": access_token, "refresh_token": refresh_token}

# -------------------------
# Logout (optional, token blacklisting can be implemented)
# -------------------------
@router.post("/logout")
def logout():
    return {"message": "Logout successful (client should discard tokens)"}
