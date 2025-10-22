from fastapi import APIRouter
from bson import ObjectId
from db import get_db
from datetime import datetime

router = APIRouter(prefix="/api/search", tags=["search"])
db = get_db()

def text_score(f, q):
    if not q: return 0.5
    q = q.lower()
    combined = f"{f['from']} {f['to']} {f['airline']}".lower()
    score = 0
    if q in combined: score += 0.7
    for token in q.split():
        if token in combined: score += 0.2
    return min(1, score)

def recency_score(ts):
    if not ts: return 0.1
    diff_hours = (datetime.utcnow() - ts).total_seconds() / 3600
    return max(0.01, 1 - min(1, diff_hours / 72))

def date_proximity_score(target, flight_date):
    if not target: return 0.5
    diff_days = abs((flight_date - target).days)
    return max(0.01, 1 - min(1, diff_days / 180))

@router.get("/")
def hybrid_search(q: str = "", limit: int = 10):
    flights = list(db.flights.find())
    results = []
    for f in flights:
        latest = db.pricepoints.find_one({"flight": f["_id"]}, sort=[("timestamp", -1)])
        latest_price = latest["priceUSD"] if latest else None
        t = text_score(f, q)
        r = recency_score(latest["timestamp"] if latest else None)
        d = date_proximity_score(datetime.utcnow(), f["flightDate"])
        score = 0.5 * t + 0.25 * r + 0.25 * d
        results.append({
            "flight": {
                "_id": str(f["_id"]),
                "from": f["from"],
                "to": f["to"],
                "airline": f["airline"],
                "flightDate": f["flightDate"]
            },
            "latestPrice": latest_price,
            "score": score
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"ok": True, "results": results[:limit]}
