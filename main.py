from fastapi import FastAPI
from routes import flights, search
from db import get_db
from scheduler import run_scheduler
import os

app = FastAPI(title="Flight Price Tracker")

app.include_router(flights.router)
app.include_router(search.router)

@app.get("/")
def home():
    return {"message": "Flight Price Tracker API"}

# Start scheduler
db = get_db()
run_scheduler(db)
