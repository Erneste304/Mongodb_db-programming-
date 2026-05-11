from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import List
from backend.core.config import settings
from backend.models.user import User, Role, Permission, UserPermission
from backend.models.audit_log import AuditLog
from backend.models.approval_request import ApprovalRequest
from backend.models.sales import Transaction, Customer
from backend.models.inventory import Tank, FuelDelivery, InventoryRecord
from backend.models.finance import Payment, DailyCashReconciliation, PettyCash
from backend.models.pricing import FuelPricing, PartnerAgreement
from backend.models.system_settings import SystemSettings
from backend.models.staff_management import (
    StaffSchedule, AttendanceRecord, Timesheet,
    StationOperationLog, SafetyComplianceRecord,
    PumpCalibrationRecord, SupplierDelivery, CustomerComplaint
)
from backend.models.accounting import (
    BankReconciliation, AccountsReceivable, AccountsPayable,
    TaxRecord, FuelCostTracking, CommissionCalculation,
    CorporateInvoice, DailyClosing, RURAComplianceReport
)


class Database:
    client: AsyncIOMotorClient = None
    
    def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        print(f"Connected to MongoDB at {settings.MONGODB_URI}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")
    
    async def init_beanie(self):
        """Initialize Beanie ODM"""
        await init_beanie(
            database=self.client[settings.DATABASE_NAME],
            document_models=[
                User,
                Role,
                Permission,
                UserPermission,
                AuditLog,
                ApprovalRequest,
                Transaction,
                Customer,
                Tank,
                FuelDelivery,
                InventoryRecord,
                Payment,
                DailyCashReconciliation,
                PettyCash,
                FuelPricing,
                PartnerAgreement,
                SystemSettings,
                StaffSchedule,
                AttendanceRecord,
                Timesheet,
                StationOperationLog,
                SafetyComplianceRecord,
                PumpCalibrationRecord,
                SupplierDelivery,
                CustomerComplaint,
                BankReconciliation,
                AccountsReceivable,
                AccountsPayable,
                TaxRecord,
                FuelCostTracking,
                CommissionCalculation,
                CorporateInvoice,
                DailyClosing,
                RURAComplianceReport
            ]
        )
        print("Initialized Beanie ODM")


db = Database()
