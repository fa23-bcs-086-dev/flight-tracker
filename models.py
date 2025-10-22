from datetime import datetime

def flight_doc(airline, from_code, to_code, flight_date, tracking_start, tracking_interval_minutes=10080):
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

def pricepoint_doc(flight_id, price_usd, timestamp=None, source="simulator"):
    return {
        "flight": flight_id,
        "timestamp": timestamp or datetime.utcnow(),
        "priceUSD": price_usd,
        "source": source
    }
