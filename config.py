import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # MongoDB Atlas Connection
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://petroleum_user:StrongPassword123!@cluster0.xxxxx.mongodb.net/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'petroleum_station_cloud')
    
    # Collection Names
    COLLECTIONS = {
        'stations': 'stations',
        'employees': 'employees',
        'customers': 'customers',
        'sales': 'sales',
        'fuel_types': 'fuel_types',
        'inventory': 'inventory',
        'customer_loyalty': 'customer_loyalty'
    }
    
    # Application Settings
    APP_NAME = "Petroleum Station Cloud Database"
    VERSION = "1.0.0"
