import json
from datetime import datetime
from db import db
from bson import ObjectId

with open("flights_seed.json") as f:
    flights = json.load(f)

db.flights.delete_many({})
db.pricepoints.delete_many({})

for f in flights:
    f["flightDate"] = datetime.fromisoformat(f["flightDate"].replace("Z", "+00:00"))
    f["trackingStart"] = datetime.fromisoformat(f["trackingStart"].replace("Z", "+00:00"))
    db.flights.insert_one(f)

print("✅ Seed data inserted successfully.")
