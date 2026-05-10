import asyncio
import sys
import os
from datetime import datetime
from passlib.context import CryptContext

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import db
from backend.models.user import User, Role
from backend.models.audit_log import AuditLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_superadmin():
    """Create initial superadmin user"""
    
    # Get or create superadmin role
    superadmin_role = await Role.find_one(Role.name == "superadmin")
    if not superadmin_role:
        print("Superadmin role not found. Please run seed_roles_permissions.py first.")
        return
    
    # Check if superadmin already exists
    existing_superadmin = await User.find_one(User.username == "superadmin")
    if existing_superadmin:
        print("Superadmin user already exists.")
        return
    
    # Create superadmin user
    password_hash = pwd_context.hash("admin123")  # Change this in production!
    superadmin = User(
        username="superadmin",
        email="admin@petrolstation.rw",
        password_hash=password_hash,
        role=superadmin_role,
        full_name="System Administrator",
        employee_id="SA-001",
        phone="+250788123456",
        is_active=True,
        created_by="system",
        created_at=datetime.utcnow()
    )
    
    await superadmin.insert()
    
    # Log the creation
    audit_log = AuditLog(
        user_id=str(superadmin.id),
        action="created_user",
        resource_type="user",
        resource_id=str(superadmin.id),
        old_value={},
        new_value={
            "username": superadmin.username,
            "role": superadmin.role.name,
            "created_by": "system"
        },
        timestamp=datetime.utcnow(),
        visible_to_roles=[1]  # Only superadmin can see
    )
    await audit_log.insert()
    
    print("Superadmin user created successfully!")
    print("Username: superadmin")
    print("Password: admin123")
    print("⚠️  IMPORTANT: Change the password after first login!")


async def main():
    """Main seed function"""
    db.connect()
    await db.init_beanie()
    
    await create_superadmin()
    
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
