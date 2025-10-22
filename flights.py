from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from db import get_db

router = APIRouter(prefix="/api/flights", tags=["flights"])
db = get_db()

@router.post("/")
def create_flight(flight: dict):
    try:
        flight["flightDate"] = datetime.fromisoformat(flight["flightDate"])
        flight["trackingStart"] = datetime.fromisoformat(flight["trackingStart"])
        result = db.flights.insert_one(flight)
        return {"ok": True, "flight_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/{flight_id}")
def get_flight(flight_id: str):
    f = db.flights.find_one({"_id": ObjectId(flight_id)})
    if not f:
        raise HTTPException(404, "Flight not found")
    f["_id"] = str(f["_id"])
    return f

@router.get("/{flight_id}/prices")
def get_prices(flight_id: str):
    points = list(db.pricepoints.find({"flight": ObjectId(flight_id)}).sort("timestamp", 1))
    for p in points:
        p["_id"] = str(p["_id"])
        p["flight"] = str(p["flight"])
    return {"ok": True, "points": points}
