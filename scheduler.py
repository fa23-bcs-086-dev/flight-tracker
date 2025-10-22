from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from utils.price_simulator import simulate_price
from bson import ObjectId

def run_scheduler(db):
    scheduler = BackgroundScheduler()
    
    def update_prices():
        now = datetime.utcnow()
        flights = list(db.flights.find({"active": True, "trackingStart": {"$lte": now}, "flightDate": {"$gt": now}}))
        
        for f in flights:
            days_until = (f["flightDate"] - now).days
            route_factor = (len(f["from"]) + len(f["to"])) % 300 + 200
            base_price = max(100, route_factor)
            count = db.pricepoints.count_documents({"flight": f["_id"]})
            price = simulate_price(base_price, days_until, count)
            db.pricepoints.insert_one({
                "flight": f["_id"],
                "priceUSD": price,
                "timestamp": now,
                "source": "simulator"
            })
            print(f"[Scheduler] {f['airline']} {f['from']}→{f['to']} price = ${price}")
    
    # every minute for demo
    scheduler.add_job(update_prices, "interval", minutes=1)
    scheduler.start()
    print("Scheduler started")
