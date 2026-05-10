from database import db_instance
from datetime import datetime
from bson import ObjectId
import random

class CRUDOperations:
    """Complete CRUD Operations for Cloud Database"""
    
    def __init__(self):
        self.db = db_instance
    
    # ============ STATION OPERATIONS ============
    
    def create_station(self, station_data):
        """Create a new station"""
        collection = self.db.get_collection('stations')
        
        # Generate auto-increment ID
        last_station = collection.find_one(sort=[('station_id', -1)])
        new_id = (last_station['station_id'] + 1) if last_station else 1
        
        station_data['station_id'] = new_id
        station_data['created_at'] = datetime.now()
        station_data['updated_at'] = datetime.now()
        station_data['status'] = station_data.get('status', 'Active')
        
        result = collection.insert_one(station_data)
        print(f"✅ Station created with ID: {new_id}")
        return result.inserted_id
    
    def get_all_stations(self, limit=100):
        """Retrieve all stations"""
        collection = self.db.get_collection('stations')
        stations = list(collection.find({}).limit(limit))
        print(f"📋 Retrieved {len(stations)} stations")
        return stations
    
    def get_station_by_id(self, station_id):
        """Get station by ID"""
        collection = self.db.get_collection('stations')
        station = collection.find_one({'station_id': station_id})
        return station
    
    def update_station(self, station_id, update_data):
        """Update station information"""
        collection = self.db.get_collection('stations')
        update_data['updated_at'] = datetime.now()
        
        result = collection.update_one(
            {'station_id': station_id},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Station {station_id} updated successfully")
        return result.modified_count
    
    def delete_station(self, station_id):
        """Delete a station"""
        collection = self.db.get_collection('stations')
        result = collection.delete_one({'station_id': station_id})
        
        if result.deleted_count > 0:
            print(f"✅ Station {station_id} deleted successfully")
        return result.deleted_count
    
    def search_stations(self, keyword):
        """Search stations by name or location"""
        collection = self.db.get_collection('stations')
        results = collection.find({
            '$or': [
                {'station_name': {'$regex': keyword, '$options': 'i'}},
                {'location': {'$regex': keyword, '$options': 'i'}}
            ]
        })
        return list(results)
    
    # ============ SALES OPERATIONS ============
    
    def create_sale(self, sale_data):
        """Record a new sale with automatic discount calculation"""
        collection = self.db.get_collection('sales')
        
        # Generate invoice number
        last_sale = collection.find_one(sort=[('sale_id', -1)])
        new_id = (last_sale['sale_id'] + 1) if last_sale else 1
        sale_data['sale_id'] = new_id
        sale_data['invoice_number'] = f"INV-{datetime.now().strftime('%Y%m%d')}-{new_id:04d}"
        sale_data['sale_date'] = datetime.now()
        sale_data['status'] = 'Completed'
        
        # Calculate discounts based on volume
        quantity = sale_data.get('quantity', 0)
        subtotal = sale_data.get('total_amount', 0)
        
        discount_percentage = 0
        if quantity >= 10000:
            discount_percentage = 10
        elif quantity >= 5000:
            discount_percentage = 7.5
        elif quantity >= 1000:
            discount_percentage = 5
        elif quantity >= 500:
            discount_percentage = 2.5
        
        discount_amount = subtotal * (discount_percentage / 100)
        sale_data['discount_amount'] = discount_amount
        sale_data['net_amount'] = subtotal - discount_amount
        
        result = collection.insert_one(sale_data)
        print(f"💰 Sale recorded: {sale_data['invoice_number']}")
        print(f"   Subtotal: RWF {subtotal:,.2f}")
        print(f"   Discount: {discount_percentage}% (RWF {discount_amount:,.2f})")
        print(f"   Net Total: RWF {sale_data['net_amount']:,.2f}")
        
        # Update inventory after sale
        self.update_inventory(sale_data['fuel_type'], quantity, is_sale=True)
        
        # Update customer loyalty if customer exists
        if sale_data.get('customer_id'):
            self.update_customer_loyalty(sale_data['customer_id'], sale_data['net_amount'], quantity)
        
        return result.inserted_id
    
    def get_sales_report(self, start_date=None, end_date=None):
        """Get sales report for date range"""
        collection = self.db.get_collection('sales')
        
        query = {}
        if start_date and end_date:
            query['sale_date'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        
        sales = list(collection.find(query).sort('sale_date', -1))
        
        # Calculate summary
        total_sales = len(sales)
        total_revenue = sum(s.get('net_amount', 0) for s in sales)
        total_quantity = sum(s.get('quantity', 0) for s in sales)
        total_discount = sum(s.get('discount_amount', 0) for s in sales)
        
        return {
            'sales': sales,
            'summary': {
                'total_transactions': total_sales,
                'total_revenue': total_revenue,
                'total_liters': total_quantity,
                'total_discount': total_discount,
                'average_sale': total_revenue / total_sales if total_sales > 0 else 0
            }
        }
    
    # ============ CUSTOMER & LOYALTY OPERATIONS ============
    
    def create_customer(self, customer_data):
        """Create new customer with loyalty tracking"""
        collection = self.db.get_collection('customers')
        
        # Generate customer ID
        last_customer = collection.find_one(sort=[('customer_id', -1)])
        new_id = (last_customer['customer_id'] + 1) if last_customer else 1
        
        customer_data['customer_id'] = new_id
        customer_data['created_at'] = datetime.now()
        customer_data['loyalty_tier'] = 'Bronze'
        customer_data['loyalty_points'] = 0
        customer_data['total_spent'] = 0
        
        result = collection.insert_one(customer_data)
        print(f"👤 Customer created: {customer_data['name']} (ID: {new_id})")
        
        # Initialize loyalty record
        self.init_customer_loyalty(new_id, customer_data['name'])
        
        return result.inserted_id
    
    def init_customer_loyalty(self, customer_id, customer_name):
        """Initialize loyalty tracking for new customer"""
        collection = self.db.get_collection('customer_loyalty')
        
        loyalty_data = {
            'customer_id': customer_id,
            'customer_name': customer_name,
            'total_purchases': 0,
            'total_liters': 0,
            'total_spent': 0,
            'points_balance': 0,
            'tier': 'Bronze',
            'discount_percentage': 0,
            'created_at': datetime.now()
        }
        
        collection.insert_one(loyalty_data)
        print(f"⭐ Loyalty tracking initialized for {customer_name}")
    
    def update_customer_loyalty(self, customer_id, amount_spent, liters):
        """Update customer loyalty points and tier"""
        collection = self.db.get_collection('customer_loyalty')
        
        # Calculate points (1 point per 1000 RWF)
        points_earned = int(amount_spent / 1000)
        
        # Get current loyalty record
        loyalty = collection.find_one({'customer_id': customer_id})
        
        if loyalty:
            total_spent = loyalty.get('total_spent', 0) + amount_spent
            total_liters = loyalty.get('total_liters', 0) + liters
            total_purchases = loyalty.get('total_purchases', 0) + 1
            points_balance = loyalty.get('points_balance', 0) + points_earned
            
            # Determine tier based on total liters
            if total_liters >= 10000:
                tier = 'Diamond'
                discount = 10.0
            elif total_liters >= 5000:
                tier = 'Platinum'
                discount = 7.5
            elif total_liters >= 2000:
                tier = 'Gold'
                discount = 5.0
            elif total_liters >= 500:
                tier = 'Silver'
                discount = 2.5
            else:
                tier = 'Bronze'
                discount = 0
            
            # Update loyalty record
            collection.update_one(
                {'customer_id': customer_id},
                {'$set': {
                    'total_spent': total_spent,
                    'total_liters': total_liters,
                    'total_purchases': total_purchases,
                    'points_balance': points_balance,
                    'tier': tier,
                    'discount_percentage': discount,
                    'last_purchase_date': datetime.now()
                }}
            )
            
            # Check for tier upgrade notification
            if tier != loyalty.get('tier'):
                print(f"🎉 CONGRATULATIONS! {loyalty.get('customer_name')} upgraded to {tier} tier!")
                print(f"   Now enjoying {discount}% discount on all purchases!")
    
    def get_top_customers(self, limit=10):
        """Get top customers by spending"""
        collection = self.db.get_collection('customer_loyalty')
        top_customers = list(collection.find().sort('total_spent', -1).limit(limit))
        
        print(f"\n🏆 TOP {len(top_customers)} CUSTOMERS:")
        print("-" * 60)
        for i, customer in enumerate(top_customers, 1):
            print(f"{i}. {customer['customer_name']}")
            print(f"   💰 Spent: RWF {customer['total_spent']:,.2f}")
            print(f"   ⭐ Points: {customer['points_balance']}")
            print(f"   👑 Tier: {customer['tier']} ({customer['discount_percentage']}% off)")
            print("-" * 40)
        
        return top_customers
    
    # ============ INVENTORY OPERATIONS ============
    
    def update_inventory(self, fuel_name, quantity, is_sale=False):
        """Update inventory levels after sale or delivery"""
        collection = self.db.get_collection('inventory')
        
        inventory = collection.find_one({'fuel_name': fuel_name})
        
        if inventory:
            if is_sale:
                new_stock = inventory['current_stock'] - quantity
                change_type = "SALE"
            else:
                new_stock = inventory['current_stock'] + quantity
                change_type = "DELIVERY"
            
            collection.update_one(
                {'fuel_name': fuel_name},
                {'$set': {
                    'current_stock': new_stock,
                    'last_updated': datetime.now()
                }}
            )
            
            # Check for low stock alert
            if new_stock <= inventory.get('reorder_level', 0):
                print(f"⚠️ LOW STOCK ALERT: {fuel_name} is at {new_stock:,.0f} L")
                print(f"   Reorder level: {inventory['reorder_level']:,.0f} L")
            
            print(f"📦 Inventory updated: {fuel_name}")
            print(f"   {change_type}: {quantity:,.0f} L")
            print(f"   New Stock: {new_stock:,.0f} L")
    
    def get_low_stock_items(self):
        """Get all items with low stock"""
        collection = self.db.get_collection('inventory')
        low_stock = list(collection.find({
            '$expr': {
                '$lte': ['$current_stock', '$reorder_level']
            }
        }))
        
        if low_stock:
            print("\n⚠️ LOW STOCK ITEMS:")
            for item in low_stock:
                print(f"   • {item['fuel_name']}: {item['current_stock']:,.0f} L (Reorder at {item['reorder_level']:,.0f} L)")
        
        return low_stock
    
    # ============ AGGREGATION & ANALYTICS ============
    
    def get_sales_by_fuel_type(self):
        """Get sales grouped by fuel type"""
        collection = self.db.get_collection('sales')
        
        pipeline = [
            {'$group': {
                '_id': '$fuel_type',
                'total_liters': {'$sum': '$quantity'},
                'total_revenue': {'$sum': '$net_amount'},
                'transaction_count': {'$sum': 1}
            }},
            {'$sort': {'total_revenue': -1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        print("\n📊 SALES BY FUEL TYPE")
        print("-" * 50)
        for result in results:
            print(f"{result['_id']}:")
            print(f"   Liters: {result['total_liters']:,.0f} L")
            print(f"   Revenue: RWF {result['total_revenue']:,.2f}")
            print(f"   Transactions: {result['transaction_count']}")
        
        return results
    
    def get_daily_sales_trend(self, days=7):
        """Get daily sales trend for last N days"""
        from datetime import timedelta
        
        collection = self.db.get_collection('sales')
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        pipeline = [
            {
                '$match': {
                    'sale_date': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {'format': '%Y-%m-%d', 'date': '$sale_date'}
                    },
                    'daily_revenue': {'$sum': '$net_amount'},
                    'daily_liters': {'$sum': '$quantity'},
                    'transaction_count': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        
        results = list(collection.aggregate(pipeline))
        
        print(f"\n📈 DAILY SALES TREND (Last {days} days)")
        print("-" * 60)
        for result in results:
            print(f"{result['_id']}:")
            print(f"   Revenue: RWF {result['daily_revenue']:,.2f}")
            print(f"   Liters: {result['daily_liters']:,.0f} L")
            print(f"   Transactions: {result['transaction_count']}")
        
        return results
    
    def get_database_summary(self):
        """Get complete database summary"""
        stations = self.db.get_collection('stations').count_documents({})
        employees = self.db.get_collection('employees').count_documents({})
        customers = self.db.get_collection('customers').count_documents({})
        sales = self.db.get_collection('sales').count_documents({})
        
        # Get total revenue
        revenue_pipeline = [
            {'$group': {
                '_id': None,
                'total_revenue': {'$sum': '$net_amount'},
                'total_liters': {'$sum': '$quantity'}
            }}
        ]
        revenue_result = list(self.db.get_collection('sales').aggregate(revenue_pipeline))
        total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
        total_liters = revenue_result[0]['total_liters'] if revenue_result else 0
        
        print("\n" + "="*60)
        print("📊 CLOUD DATABASE SUMMARY")
        print("="*60)
        print(f"🏪 Stations: {stations}")
        print(f"👥 Employees: {employees}")
        print(f"👤 Customers: {customers}")
        print(f"💰 Total Sales: {sales}")
        print(f"💵 Total Revenue: RWF {total_revenue:,.2f}")
        print(f"⛽ Total Liters Sold: {total_liters:,.0f} L")
        print("="*60)
        
        return {
            'stations': stations,
            'employees': employees,
            'customers': customers,
            'sales': sales,
            'total_revenue': total_revenue,
            'total_liters': total_liters
        }
