# app/dependencies.py
from fastapi import Header, HTTPException, status
from app.auth import verify_token

from app.db.base import SessionLocal

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role-based access dependency
def require_role(token: str = Header(...), allowed_roles: list = []):
    if token.startswith("Bearer "):
        token = token[7:]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    role = payload.get("role", "User")
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized for this role")
    return payload
