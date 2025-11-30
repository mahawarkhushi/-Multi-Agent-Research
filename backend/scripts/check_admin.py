# backend/scripts/check_admin.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.db.user import User

# Open DB session
db = SessionLocal()

# Check for Admin user
admin_email = "admin@example.com"
admin = db.query(User).filter(User.email == admin_email).first()

if admin:
    print(f"Admin exists: Email={admin.email}, Role={admin.role}, Active={admin.is_active}")
else:
    print("Admin user not found.")

db.close()