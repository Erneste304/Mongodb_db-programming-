from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi
from config import Config
from beanie import init_beanie
# Import all your Beanie Document models
from backend.models.user import User, Role, Permission, UserPermission
from backend.models.accounting import (
    BankReconciliation, AccountsReceivable, AccountsPayable,
    TaxRecord, FuelCostTracking, CommissionCalculation,
    CorporateInvoice, DailyClosing, RURAComplianceReport
)
import time

class CloudDatabase:
    """MongoDB Atlas Cloud Database Connection Manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False
        
    def connect(self, max_retries=3):
        """Establish connection to MongoDB Atlas"""
        for attempt in range(max_retries):
            try:
                print(f"🔗 Attempting to connect to MongoDB Atlas (Attempt {attempt + 1})...")
                
                # Connect with SSL certificate
                self.client = MongoClient(
                    Config.MONGODB_URI,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000
                )
                
                # Test connection
                self.client.admin.command('ping')
                
                # Select database
                self.db = self.client[Config.DATABASE_NAME]
                self.connected = True
                
                print("✅ Successfully connected to MongoDB Atlas!")
                print(f"📊 Database: {Config.DATABASE_NAME}")
                print(f"🌍 Cluster: {self.client.nodes}")
                
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("❌ Failed to connect after all retries.")
                    return False
        
        return False
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if not self.connected:
            raise Exception("Database not connected. Call connect() first.")
        return self.db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("🔒 Database connection closed.")
    
    def get_stats(self):
        """Get database statistics"""
        if not self.connected:
            return {}
        
        stats = {
            'database_name': Config.DATABASE_NAME,
            'collections': {}
        }
        
        for name, coll_name in Config.COLLECTIONS.items():
            collection = self.db[coll_name]
            stats['collections'][name] = collection.count_documents({})
        
        return stats

# Singleton instance
db_instance = CloudDatabase()
