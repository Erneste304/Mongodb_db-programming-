from datetime import datetime
from typing import Optional, List, Dict
from pymongo import ASCENDING, DESCENDING, TEXT

class Station:
    """Station Model"""
    
    @staticmethod
    def get_schema():
        return {
            'station_id': int,
            'station_name': str,
            'location': str,
            'phone': str,
            'email': str,
            'manager_name': str,
            'opening_time': str,
            'closing_time': str,
            'status': str,  # Active, Inactive
            'created_at': datetime,
            'updated_at': datetime
        }
    
    @staticmethod
    def create_indexes(collection):
        """Create indexes for better query performance"""
        collection.create_index([('station_name', ASCENDING)])
        collection.create_index([('location', TEXT)], default_language='english')
        collection.create_index([('status', ASCENDING)])

class Sale:
    """Sale Model"""
    
    @staticmethod
    def get_schema():
        return {
            'sale_id': int,
            'invoice_number': str,
            'customer_id': Optional[int],
            'employee_id': int,
            'fuel_type': str,
            'quantity': float,
            'unit_price': float,
            'total_amount': float,
            'discount_amount': float,
            'net_amount': float,
            'payment_method': str,
            'sale_date': datetime,
            'status': str
        }
    
    @staticmethod
    def create_indexes(collection):
        collection.create_index([('sale_date', DESCENDING)])
        collection.create_index([('customer_id', ASCENDING)])
        collection.create_index([('invoice_number', ASCENDING)], unique=True)
        collection.create_index([('sale_date', DESCENDING), ('status', ASCENDING)])

class CustomerLoyalty:
    """Customer Loyalty Model"""
    
    @staticmethod
    def get_schema():
        return {
            'customer_id': int,
            'customer_name': str,
            'total_purchases': int,
            'total_liters': float,
            'total_spent': float,
            'points_balance': int,
            'tier': str,  # Bronze, Silver, Gold, Platinum, Diamond
            'discount_percentage': float,
            'last_purchase_date': datetime,
            'created_at': datetime
        }
    
    @staticmethod
    def create_indexes(collection):
        collection.create_index([('points_balance', DESCENDING)])
        collection.create_index([('tier', ASCENDING)])
        collection.create_index([('total_spent', DESCENDING)])

class Inventory:
    """Inventory Model"""
    
    @staticmethod
    def get_schema():
        return {
            'fuel_id': int,
            'fuel_name': str,
            'current_stock': float,
            'capacity': float,
            'reorder_level': float,
            'unit_price': float,
            'last_updated': datetime,
            'status': str
        }
    
    @staticmethod
    def create_indexes(collection):
        collection.create_index([('fuel_name', ASCENDING)], unique=True)
        collection.create_index([('current_stock', ASCENDING)])
