# Cloud Databases: MongoDB Atlas + Python Implementation

## Petroleum Station Management System - Cloud Database Edition

### Project Overview
This project demonstrates cloud database implementation using MongoDB Atlas and Python, featuring a complete petroleum station management system with:

- Full CRUD operations
- Automatic discount calculation
- Customer loyalty program
- Real-time inventory management
- Sales analytics and reporting

---

## Technology Stack
- **Database**: MongoDB Atlas (Cloud)
- **Language**: Python 3.9+
- **Driver**: PyMongo
- **Libraries**: python-dotenv, certifi, dnspython

---

## Project Structure
```
cloud-database-project/
├── config.py              # Configuration settings
├── database.py            # Database connection manager
├── models.py              # Data models and schemas
├── crud_operations.py     # CRUD operations
├── main.py                # Main application entry point
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (template)
└── README.md              # Documentation
```

---

## Setup Instructions

### 1. MongoDB Atlas Setup

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for a free account
3. Create a new cluster:
   - Choose **M0 (Free Tier)**
   - Select a cloud provider (AWS, GCP, or Azure)
   - Choose the closest region
4. Configure Database Access:
   - Create a database user with username and password
   - Set privileges to "Read and write to any database"
5. Configure Network Access:
   - Add IP address: `0.0.0.0/0` (for development) or your specific IP
6. Get Connection String:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

### 2. Python Environment Setup

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file with your MongoDB Atlas connection string:

```env
MONGODB_URI=mongodb+srv://your_username:your_password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=petroleum_station_cloud
```

### 4. Run the Application

```bash
python main.py
```

---

## Features

### 1. Station Management
- Create, read, update, and delete station records
- Search stations by name or location
- Track station information (location, manager, hours)

### 2. Customer Management
- Customer registration with vehicle details
- Automatic loyalty program enrollment
- Contact information management

### 3. Sales Management
- Record fuel sales with automatic invoice generation
- Volume-based discount calculation:
  - 500L+ = 2.5% discount
  - 1,000L+ = 5% discount
  - 5,000L+ = 7.5% discount
  - 10,000L+ = 10% discount
- Multiple payment methods (Cash, Mobile Money, Card)

### 4. Loyalty Program
- Points system: 1 point per 1,000 RWF spent
- Tier-based discounts:
  - Bronze: 0% (starting tier)
  - Silver: 2.5% (500L+)
  - Gold: 5% (2,000L+)
  - Platinum: 7.5% (5,000L+)
  - Diamond: 10% (10,000L+)
- Automatic tier upgrades

### 5. Inventory Management
- Real-time stock tracking
- Low stock alerts (below reorder level)
- Automatic inventory update after sales

### 6. Reports & Analytics
- Sales by fuel type
- Daily sales trends
- Customer ranking by spending
- Complete database summary

---

## Usage

### Main Menu Options

| Option | Description |
|--------|-------------|
| 1 | Station Management - Add/view/search/update/delete stations |
| 2 | Customer Management - Register new customers |
| 3 | Sales Management - Record sales with auto-discount |
| 4 | Loyalty Program - Check customer tier and points |
| 5 | Reports & Analytics - Sales reports and trends |
| 6 | Inventory Management - Check low stock items |
| 7 | Top Customers - View customers ranked by spending |
| 8 | Database Summary - Complete statistics |
| 9 | Test Data Generation - Create sample data for demo |
| 0 | Exit - Close application |

### Quick Start Demo

1. Run the application: `python main.py`
2. Select option `9` to generate test data
3. Select option `3` to record a sale
4. Select option `4` to check customer loyalty
5. Select option `8` to view database summary

---

## Cloud Database Concepts

### What is a Cloud Database?
A cloud database is a database service built, deployed, and accessed through a cloud computing platform. It eliminates the need for on-premise hardware and infrastructure management.

### Key Characteristics
- **Elasticity**: Auto-scaling based on demand
- **High Availability**: 99.99% uptime SLA
- **Managed Service**: Automatic backups, patches, updates
- **Pay-per-use**: Only pay for consumed resources
- **Global Access**: Access from anywhere via internet

### Deployment Models
- **IaaS**: You manage the database on cloud infrastructure
- **PaaS**: Provider manages infrastructure, you manage database
- **DBaaS**: Fully managed database service

### Major Providers
| Provider | SQL Services | NoSQL Services |
|----------|--------------|----------------|
| AWS | RDS, Aurora | DynamoDB |
| Google Cloud | Cloud SQL | Firestore, Bigtable |
| Azure | SQL Database | Cosmos DB |
| MongoDB | N/A | Atlas |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Check IP whitelist (0.0.0.0/0 for development) |
| Authentication failed | Verify username/password in connection string |
| Module not found | Run `pip install -r requirements.txt` |
| Database not created | Atlas auto-creates on first write |
| SSL certificate error | Ensure `certifi` package is installed |

---

## Author
Cloud Databases Assignment - MongoDB Atlas + Python Implementation

---

## License
This project is for educational purposes.
