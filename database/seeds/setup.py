"""
Master setup script for Petroleum Station Management System
This script initializes the database with all required data.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import database first
from backend.core.database import db

async def setup_database():
    """Run complete database setup"""
    print("=" * 60)
    print("Petroleum Station Management System - Database Setup")
    print("=" * 60)
    print()
    
    try:
        # Initialize Beanie ODM first
        print("Initializing database connection...")
        await db.init_beanie()
        print("✓ Database initialized")
        print()
        
        # Now import seed functions after Beanie is initialized
        from database.seeds.seed_roles_permissions import seed_roles, seed_permissions
        from database.seeds.seed_superadmin import create_superadmin
        
        # Step 1: Seed roles
        print("Step 1/3: Seeding roles...")
        await seed_roles()
        print("✓ Roles seeded successfully")
        print()
        
        # Step 2: Seed permissions
        print("Step 2/3: Seeding permissions...")
        await seed_permissions()
        print("✓ Permissions seeded successfully")
        print()
        
        # Step 3: Create superadmin user
        print("Step 3/3: Creating superadmin user...")
        await create_superadmin()
        print()
        
        print("=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)
        print()
        print("IMPORTANT NOTES:")
        print("1. Default superadmin credentials:")
        print("   Username: superadmin")
        print("   Password: admin123")
        print("   ⚠️  CHANGE THE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
        print()
        print("2. Roles created:")
        print("   - superadmin (Level 1)")
        print("   - admin (Level 2)")
        print("   - accountant (Level 3)")
        print("   - receptionist (Level 4)")
        print("   - inventory_manager (Level 4)")
        print("   - staff (Level 5)")
        print("   - customer (Level 6)")
        print()
        print("3. Permissions created for:")
        print("   - User management (create, read, update, delete)")
        print("   - Sales operations (create, read, void)")
        print("   - Inventory management (read, update)")
        print("   - Financial operations (read, process, reports)")
        print("   - Reports (sales, inventory, audit)")
        print("   - Settings (pricing, permissions)")
        print()
        
    except Exception as e:
        import traceback
        print(f"✗ Setup failed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    from datetime import datetime
    
    # Connect to database
    db.connect()
    
    # Run setup
    asyncio.run(setup_database())
    
    # Close connection
    db.close()
