from datetime import datetime
from typing import Any
from bson import ObjectId


def flight_doc(
    airline: str,
    from_code: str,
    to_code: str,
    flight_date: datetime,
    tracking_start: datetime,
    tracking_interval_minutes: int = 10080,
) -> dict:
    """Create a flight document for insertion into MongoDB."""
    return {
        "airline": airline,
        "from": from_code,
        "to": to_code,
        "flightDate": flight_date,
        "trackingStart": tracking_start,
        "trackingIntervalMinutes": tracking_interval_minutes,
        "active": True,
        "createdAt": datetime.utcnow(),
    }


def pricepoint_doc(flight_id: Any, price_usd: float, timestamp: datetime = None, source: str = "simulator") -> dict:
    """Create a pricepoint document. flight_id can be str or ObjectId."""
    fid = ObjectId(flight_id) if not isinstance(flight_id, ObjectId) else flight_id
    return {
        "flight": fid,
        "timestamp": timestamp or datetime.utcnow(),
        "priceUSD": float(price_usd),
        "source": source,
    }