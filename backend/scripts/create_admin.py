# backend/scripts/create_admin.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.db.user import User
from app.auth import hash_password

db = SessionLocal()

# Admin credentials
admin_email = "admin@example.com"
admin_password = "adminpass"

# Check if admin exists
existing_admin = db.query(User).filter(User.email==admin_email).first()
if not existing_admin:
    admin_user = User(
        email=admin_email,
        hashed_password = hash_password(admin_password[:72]),
        role="Admin"
    )
    db.add(admin_user)
    db.commit()
    print(f"Admin user created: {admin_email}")
else:
    print(f"Admin user already exists: {admin_email}")

db.close()
