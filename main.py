#!/usr/bin/env python3
"""
Petroleum Station Management System - Cloud Database Edition
MongoDB Atlas + Python Implementation
"""

from database import db_instance
from crud_operations import CRUDOperations
from datetime import datetime
import time

def print_header():
    """Print application header"""
    print("\n" + "="*60)
    print("🏪 PETROLEUM STATION MANAGEMENT SYSTEM")
    print("☁️  Cloud Database Edition (MongoDB Atlas)")
    print("="*60)

def print_menu():
    """Print main menu"""
    print("\n📋 MAIN MENU")
    print("-"*40)
    print("1. 📍 Station Management")
    print("2. 👤 Customer Management")
    print("3. 💰 Sales Management")
    print("4. ⭐ Loyalty Program")
    print("5. 📊 Reports & Analytics")
    print("6. 📦 Inventory Management")
    print("7. 🏆 Top Customers")
    print("8. 📈 Database Summary")
    print("9. 🧪 Test Data Generation")
    print("0. 🚪 Exit")
    print("-"*40)

def station_management(crud):
    """Station Management Menu"""
    while True:
        print("\n📍 STATION MANAGEMENT")
        print("1. Add New Station")
        print("2. View All Stations")
        print("3. Search Stations")
        print("4. Update Station")
        print("5. Delete Station")
        print("0. Back to Main Menu")
        
        choice = input("\nEnter choice: ")
        
        if choice == '1':
            print("\n📝 Add New Station")
            station = {
                'station_name': input("Station Name: "),
                'location': input("Location: "),
                'phone': input("Phone: "),
                'email': input("Email: "),
                'manager_name': input("Manager Name: "),
                'opening_time': input("Opening Time (HH:MM): "),
                'closing_time': input("Closing Time (HH:MM): ")
            }
            crud.create_station(station)
            
        elif choice == '2':
            stations = crud.get_all_stations()
            print("\n🏪 ALL STATIONS")
            for s in stations:
                print(f"ID: {s['station_id']} | {s['station_name']} | {s['location']}")
                
        elif choice == '3':
            keyword = input("Search keyword: ")
            results = crud.search_stations(keyword)
            print(f"\n🔍 Found {len(results)} stations:")
            for s in results:
                print(f"   • {s['station_name']} - {s['location']}")
                
        elif choice == '4':
            station_id = int(input("Station ID to update: "))
            print("Enter new values (leave blank to keep current):")
            update_data = {}
            name = input("New Station Name: ")
            if name: update_data['station_name'] = name
            location = input("New Location: ")
            if location: update_data['location'] = location
            phone = input("New Phone: ")
            if phone: update_data['phone'] = phone
            if update_data:
                crud.update_station(station_id, update_data)
                
        elif choice == '5':
            station_id = int(input("Station ID to delete: "))
            confirm = input(f"Delete station {station_id}? (y/n): ")
            if confirm.lower() == 'y':
                crud.delete_station(station_id)
                
        elif choice == '0':
            break

def customer_management(crud):
    """Customer Management Menu"""
    print("\n👤 CUSTOMER MANAGEMENT")
    customer = {
        'name': input("Customer Name: "),
        'phone': input("Phone: "),
        'email': input("Email: "),
        'vehicle_plate': input("Vehicle Plate: "),
        'vehicle_type': input("Vehicle Type (Sedan/SUV/Pickup): "),
        'address': input("Address: ")
    }
    crud.create_customer(customer)

def sales_management(crud):
    """Sales Management Menu"""
    print("\n💰 RECORD NEW SALE")
    
    # Get available fuel types from inventory
    inventory_collection = crud.db.get_collection('inventory')
    fuel_types = list(inventory_collection.find({}))
    
    if not fuel_types:
        print("⚠️ No fuel inventory found. Please generate test data first (Option 9).")
        return
    
    print("\n⛽ Available Fuel Types:")
    for i, fuel in enumerate(fuel_types, 1):
        print(f"{i}. {fuel['fuel_name']} - RWF {fuel['unit_price']:,.2f}/L (Stock: {fuel['current_stock']:,.0f}L)")
    
    fuel_choice = int(input("\nSelect fuel type: ")) - 1
    if fuel_choice < 0 or fuel_choice >= len(fuel_types):
        print("❌ Invalid fuel type selection.")
        return
        
    selected_fuel = fuel_types[fuel_choice]
    
    quantity = float(input("Quantity (Liters): "))
    subtotal = quantity * selected_fuel['unit_price']
    
    print(f"\n💰 Subtotal: RWF {subtotal:,.2f}")
    
    # Apply volume discount
    if quantity >= 10000:
        discount = 10
    elif quantity >= 5000:
        discount = 7.5
    elif quantity >= 1000:
        discount = 5
    elif quantity >= 500:
        discount = 2.5
    else:
        discount = 0
    
    if discount > 0:
        print(f"🎉 Volume Discount: {discount}%")
        discount_amount = subtotal * discount / 100
        print(f"   Discount Amount: RWF {discount_amount:,.2f}")
        print(f"   Final Amount: RWF {subtotal - discount_amount:,.2f}")
    
    # Ask for customer
    has_customer = input("\nIs this for a registered customer? (y/n): ")
    customer_id = None
    if has_customer.lower() == 'y':
        customer_id = int(input("Customer ID: "))
    
    sale_data = {
        'customer_id': customer_id,
        'employee_id': 1,  # Default employee
        'fuel_type': selected_fuel['fuel_name'],
        'quantity': quantity,
        'unit_price': selected_fuel['unit_price'],
        'total_amount': subtotal,
        'payment_method': input("Payment Method (Cash/Mobile Money/Card): ")
    }
    
    crud.create_sale(sale_data)

def loyalty_program(crud):
    """Loyalty Program Menu"""
    print("\n⭐ LOYALTY PROGRAM")
    customer_id = int(input("Enter Customer ID: "))
    
    # Get customer loyalty info
    collection = crud.db.get_collection('customer_loyalty')
    loyalty = collection.find_one({'customer_id': customer_id})
    
    if loyalty:
        print(f"\n👤 Customer: {loyalty['customer_name']}")
        print(f"🏆 Tier: {loyalty['tier']}")
        print(f"💎 Discount: {loyalty['discount_percentage']}%")
        print(f"⭐ Points Balance: {loyalty['points_balance']}")
        print(f"💰 Total Spent: RWF {loyalty['total_spent']:,.2f}")
        print(f"⛽ Total Liters: {loyalty['total_liters']:,.0f} L")
        print(f"🛒 Total Purchases: {loyalty['total_purchases']}")
        
        # Calculate points needed for next tier
        total_liters = loyalty['total_liters']
        if total_liters < 500:
            needed = 500 - total_liters
            print(f"\n📈 Next Tier: Silver (Need {needed:,.0f} more liters)")
        elif total_liters < 2000:
            needed = 2000 - total_liters
            print(f"\n📈 Next Tier: Gold (Need {needed:,.0f} more liters)")
        elif total_liters < 5000:
            needed = 5000 - total_liters
            print(f"\n📈 Next Tier: Platinum (Need {needed:,.0f} more liters)")
        elif total_liters < 10000:
            needed = 10000 - total_liters
            print(f"\n📈 Next Tier: Diamond (Need {needed:,.0f} more liters)")
    else:
        print("❌ Customer not found in loyalty program")

def generate_test_data(crud):
    """Generate test data for demonstration"""
    print("\n🧪 GENERATING TEST DATA")
    
    # Sample stations
    stations = [
        ('Kigali Central Station', 'Kigali City Center', '0788123456', 'kigali@petroleum.com', 'John Manager'),
        ('Nyamirambo Station', 'Nyamirambo District', '0788223456', 'nyamirambo@petroleum.com', 'Alice Supervisor'),
        ('Kimironko Station', 'Kimironko Sector', '0788333456', 'kimironko@petroleum.com', 'Peter Manager')
    ]
    
    print("📍 Creating stations...")
    for station in stations:
        station_data = {
            'station_name': station[0],
            'location': station[1],
            'phone': station[2],
            'email': station[3],
            'manager_name': station[4],
            'opening_time': '06:00',
            'closing_time': '22:00'
        }
        crud.create_station(station_data)
    
    # Sample customers
    customers = [
        ('Claude Ndayisaba', '0788444444', 'claude@email.com', 'RAA123A', 'SUV'),
        ('Patrick Habimana', '0788555555', 'patrick@email.com', 'RAB456B', 'Sedan'),
        ('Marie Claire', '0788666666', 'marie@email.com', 'RAC789C', 'Pickup')
    ]
    
    print("\n👤 Creating customers...")
    for customer in customers:
        customer_data = {
            'name': customer[0],
            'phone': customer[1],
            'email': customer[2],
            'vehicle_plate': customer[3],
            'vehicle_type': customer[4],
            'address': 'Kigali, Rwanda'
        }
        crud.create_customer(customer_data)
    
    # Sample inventory
    inventory_items = [
        ('Petrol', 1500.00, 8500, 10000, 1000),
        ('Diesel', 1400.00, 7200, 12000, 1200),
        ('Super', 1600.00, 4500, 8000, 800)
    ]
    
    print("\n📦 Creating inventory...")
    inv_collection = crud.db.get_collection('inventory')
    for item in inventory_items:
        inv_collection.insert_one({
            'fuel_name': item[0],
            'unit_price': item[1],
            'current_stock': item[2],
            'capacity': item[3],
            'reorder_level': item[4],
            'last_updated': datetime.now()
        })
    
    # Sample sales
    print("\n💰 Creating sample sales...")
    sales_data = [
        (1, 'Petrol', 550, 1500),
        (2, 'Diesel', 1200, 1400),
        (1, 'Super', 2100, 1600),
        (3, 'Petrol', 5200, 1500),
        (2, 'Diesel', 11000, 1400)
    ]
    
    for sale in sales_data:
        sale_dict = {
            'customer_id': sale[0],
            'employee_id': 1,
            'fuel_type': sale[1],
            'quantity': sale[2],
            'unit_price': sale[3],
            'total_amount': sale[2] * sale[3],
            'payment_method': 'Cash',
            'sale_date': datetime.now()
        }
        crud.create_sale(sale_dict)
    
    print("\n✅ Test data generation complete!")

def main():
    """Main application entry point"""
    print_header()
    
    # Connect to MongoDB Atlas
    if not db_instance.connect():
        print("❌ Failed to connect to MongoDB Atlas. Please check your connection string.")
        return
    
    crud = CRUDOperations()
    
    while True:
        print_menu()
        choice = input("\n👉 Enter your choice: ")
        
        if choice == '1':
            station_management(crud)
        elif choice == '2':
            customer_management(crud)
        elif choice == '3':
            sales_management(crud)
        elif choice == '4':
            loyalty_program(crud)
        elif choice == '5':
            print("\n📊 REPORTS & ANALYTICS")
            print("1. Sales by Fuel Type")
            print("2. Daily Sales Trend")
            print("3. Get Sales Report")
            report_choice = input("Choice: ")
            if report_choice == '1':
                crud.get_sales_by_fuel_type()
            elif report_choice == '2':
                days = int(input("Number of days: "))
                crud.get_daily_sales_trend(days)
            elif report_choice == '3':
                crud.get_sales_report()
        elif choice == '6':
            crud.get_low_stock_items()
        elif choice == '7':
            crud.get_top_customers()
        elif choice == '8':
            crud.get_database_summary()
        elif choice == '9':
            generate_test_data(crud)
        elif choice == '0':
            print("\n👋 Thank you for using Petroleum Station Management System!")
            print("🔒 Closing database connection...")
            db_instance.close()
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
