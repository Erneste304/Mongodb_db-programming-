from pymongo import MongoClient
import certifi
import sys

# 1. Establish the connection to your local MongoDB server
# Default port for MongoDB is 27017
try:
    client = MongoClient(
        "mongodb+srv://Erneste:123@cluster0.jkte2nw.mongodb.net/?appName=Cluster0",
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000)
    # Trigger a connection test
    client.admin.command('ping')
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)

# 2. Access or create a database
db = client["university_assignment"]

# 3. Access or create a collection (similar to a table in SQL)
collection = db["test_records"]

# 4. Create a sample document to test the connection
test_doc = {
    "name": "Erneste",
    "project": "Mongodbassignment",
    "status": "connected"
}

# 5. Insert the document
try:
    result = collection.insert_one(test_doc)
    print(f"Successfully connected! Document ID: {result.inserted_id}")
except Exception as e:
    print(f"Connection failed: {e}")

# 6. Close the connection when done
client.close()
