from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.db.base import SessionLocal
from app.auth import verify_token

from fastapi import Header, HTTPException, status

# OAuth2 scheme (used for token extraction)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role-based access control dependency
def require_role(token: str, allowed_roles: list):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    role = payload.get("role", "analyst")  # default role
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized for this role")
    
    return payload

def get_token(authorization: str = Header(...)):
    # Expect header: Authorization: Bearer <token>
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid auth header")
    return authorization[7:]  # remove "Bearer " prefix
