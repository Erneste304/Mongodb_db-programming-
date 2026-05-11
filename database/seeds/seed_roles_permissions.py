import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import db
from backend.models.user import Role, Permission


async def seed_roles():
    """Create initial roles"""
    
    print("Initializing seed_roles...")
    
    roles_data = [
        {
            "name": "superadmin",
            "description": "Full system control",
            "level": 1
        },
        {
            "name": "admin",
            "description": "Operational management",
            "level": 2
        },
        {
            "name": "accountant",
            "description": "Financial management",
            "level": 3
        },
        {
            "name": "receptionist",
            "description": "Customer transactions",
            "level": 4
        },
        {
            "name": "inventory_manager",
            "description": "Stock and supply chain",
            "level": 4
        },
        {
            "name": "staff",
            "description": "General staff",
            "level": 5
        },
        {
            "name": "customer",
            "description": "Service recipient",
            "level": 6
        }
    ]
    
    for role_data in roles_data:
        try:
            print(f"Processing role: {role_data['name']}")
            existing_role = await Role.find_one(Role.name == role_data["name"])
            if not existing_role:
                print(f"Creating new role: {role_data}")
                role = Role(**role_data)
                await role.insert()
                print(f"Created role: {role_data['name']}")
            else:
                print(f"Role already exists: {role_data['name']}")
        except Exception as e:
            import traceback
            print(f"Error processing role {role_data.get('name', 'unknown')}: {e}")
            traceback.print_exc()
            raise


async def seed_permissions():
    """Create initial permissions"""
    
    permissions_data = [
        # User Management
        {
            "module": "users",
            "action": "create",
            "resource": "user",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create new users"
        },
        {
            "module": "users",
            "action": "read",
            "resource": "user",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View user information"
        },
        {
            "module": "users",
            "action": "update",
            "resource": "user",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Update user information"
        },
        {
            "module": "users",
            "action": "delete",
            "resource": "user",
            "requires_approval": True,
            "approval_role_level": 1,
            "description": "Delete users (requires superadmin approval)"
        },
        # Sales
        {
            "module": "sales",
            "action": "create",
            "resource": "transaction",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Process sales transactions"
        },
        {
            "module": "sales",
            "action": "read",
            "resource": "transaction",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View sales transactions"
        },
        {
            "module": "sales",
            "action": "void",
            "resource": "transaction",
            "requires_approval": True,
            "approval_role_level": 2,
            "description": "Void transactions (requires admin approval)"
        },
        # Inventory
        {
            "module": "inventory",
            "action": "read",
            "resource": "stock",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View inventory levels"
        },
        {
            "module": "inventory",
            "action": "update",
            "resource": "stock",
            "requires_approval": True,
            "approval_role_level": 2,
            "description": "Update inventory (requires admin approval)"
        },
        # Finance
        {
            "module": "finance",
            "action": "read",
            "resource": "transaction",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View financial transactions"
        },
        {
            "module": "finance",
            "action": "process",
            "resource": "payment",
            "requires_approval": True,
            "approval_role_level": 2,
            "description": "Process payments (requires admin approval for large amounts)"
        },
        {
            "module": "finance",
            "action": "read",
            "resource": "report",
            "requires_approval": True,
            "approval_role_level": 2,
            "description": "View financial reports (requires admin approval for historical)"
        },
        # Reports
        {
            "module": "reports",
            "action": "read",
            "resource": "sales",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View sales reports"
        },
        {
            "module": "reports",
            "action": "read",
            "resource": "inventory",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View inventory reports"
        },
        {
            "module": "reports",
            "action": "read",
            "resource": "audit",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View audit logs"
        },
        # Settings
        {
            "module": "settings",
            "action": "update",
            "resource": "pricing",
            "requires_approval": True,
            "approval_role_level": 1,
            "description": "Change fuel prices (requires superadmin approval)"
        },
        {
            "module": "settings",
            "action": "update",
            "resource": "permission",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Toggle user permissions"
        },
        # Pricing Management (Superadmin)
        {
            "module": "pricing",
            "action": "create",
            "resource": "fuel_pricing",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create fuel pricing (Superadmin only)"
        },
        {
            "module": "pricing",
            "action": "update",
            "resource": "fuel_pricing",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Update fuel pricing (Superadmin only)"
        },
        {
            "module": "pricing",
            "action": "read",
            "resource": "fuel_pricing",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View fuel pricing"
        },
        {
            "module": "pricing",
            "action": "create",
            "resource": "partner_agreement",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create partner agreements (Superadmin only)"
        },
        {
            "module": "pricing",
            "action": "read",
            "resource": "partner_agreement",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View partner agreements"
        },
        # System Settings (Superadmin)
        {
            "module": "settings",
            "action": "read",
            "resource": "system",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View system settings"
        },
        {
            "module": "settings",
            "action": "update",
            "resource": "system",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Update system settings (Superadmin only)"
        },
        {
            "module": "settings",
            "action": "update",
            "resource": "inventory_thresholds",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Configure inventory thresholds"
        },
        # Transaction Override (Superadmin)
        {
            "module": "sales",
            "action": "override",
            "resource": "transaction",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Override any transaction (Superadmin only)"
        },
        # Multi-station Management (Superadmin)
        {
            "module": "settings",
            "action": "manage",
            "resource": "stations",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Manage multiple stations (Superadmin only)"
        },
        # Staff Management (Admin)
        {
            "module": "staff",
            "action": "create",
            "resource": "schedule",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create staff schedules (Admin only)"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "schedule",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View staff schedules"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "attendance",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Record attendance (Admin only)"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "attendance",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View attendance records"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "timesheet",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Generate timesheets (Admin only)"
        },
        {
            "module": "staff",
            "action": "approve",
            "resource": "timesheet",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Approve timesheets (Admin only)"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "station_operation",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Station opening/closing (Admin only)"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "safety_inspection",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Record safety inspections (Admin only)"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "safety_inspection",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View safety inspections"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "calibration",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View pump calibrations"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "delivery_order",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create supplier delivery orders (Admin only)"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "delivery_order",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View delivery orders"
        },
        {
            "module": "staff",
            "action": "create",
            "resource": "complaint",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create customer complaints"
        },
        {
            "module": "staff",
            "action": "read",
            "resource": "complaint",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View customer complaints (Admin oversight)"
        },
        {
            "module": "staff",
            "action": "resolve",
            "resource": "complaint",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Resolve complaints (Admin only)"
        },
        # Accounting & Finance (Accountant)
        {
            "module": "accounting",
            "action": "create",
            "resource": "bank_reconciliation",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create bank reconciliations"
        },
        {
            "module": "accounting",
            "action": "read",
            "resource": "bank_reconciliation",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View bank reconciliations"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "invoice",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create corporate invoices"
        },
        {
            "module": "accounting",
            "action": "read",
            "resource": "accounts_receivable",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View accounts receivable"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "ar_payment",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Record payments from customers"
        },
        {
            "module": "accounting",
            "action": "read",
            "resource": "accounts_payable",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View accounts payable"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "ap_payment",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Record payments to suppliers"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "tax_record",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Create tax records"
        },
        {
            "module": "accounting",
            "action": "read",
            "resource": "tax_record",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "View tax records"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "cost_tracking",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Track fuel costs and margins"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "commission",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Calculate staff commissions"
        },
        {
            "module": "accounting",
            "action": "approve",
            "resource": "commission",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Approve commission payments"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "daily_closing",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Record and verify daily closing"
        },
        {
            "module": "accounting",
            "action": "create",
            "resource": "compliance_report",
            "requires_approval": False,
            "approval_role_level": None,
            "description": "Generate RURA compliance reports"
        }
    ]
    
    for perm_data in permissions_data:
        existing_perm = await Permission.find_one(
            Permission.module == perm_data["module"],
            Permission.action == perm_data["action"],
            Permission.resource == perm_data["resource"]
        )
        if not existing_perm:
            permission = Permission(**perm_data)
            await permission.insert()
            print(f"Created permission: {perm_data['module']}.{perm_data['action']}.{perm_data['resource']}")
        else:
            print(f"Permission already exists: {perm_data['module']}.{perm_data['action']}.{perm_data['resource']}")


async def main():
    """Main seed function"""
    db.connect()
    await db.init_beanie()
    
    print("Seeding roles...")
    await seed_roles()
    
    print("\nSeeding permissions...")
    await seed_permissions()
    
    print("\nSeed completed successfully!")
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
