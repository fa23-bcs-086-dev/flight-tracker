from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection(uri="mongodb://127.0.0.1:27017", db_name="Flight_track"):
    try:
        # Create Mongo client
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Attempt to connect to the server
        client.server_info()  # Force connection
        print("✅ MongoDB connection successful!")
        
        # List databases
        print("📂 Databases on this server:")
        for db_name in client.list_database_names():
            print("  -", db_name)
        
        # Check specific DB
        db = client[db_name]
        print(f"\nConnected to database: {db.name}")
        
        # List collections if exist
        if db.list_collection_names():
            print("📚 Collections in this database:")
            for collection in db.list_collection_names():
                print("  -", collection)
        else:
            print("⚠️  No collections found in this database yet.")
        
        client.close()
    except ServerSelectionTimeoutError:
        print("❌ Could not connect to MongoDB: Server timeout.")
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    test_mongodb_connection()
