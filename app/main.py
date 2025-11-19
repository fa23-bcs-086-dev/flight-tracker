from fastapi import FastAPI
from app.db.client import get_db
from app.services.scheduler import run_scheduler
from app.routes import flights, search

app = FastAPI(title="Flight Price Tracker")

# register routers (they import legacy routes if present)
app.include_router(flights.router, prefix="/api")
app.include_router(search.router, prefix="/api")


@app.get("/")
def home():
    return {"message": "Flight Price Tracker API"}


@app.on_event("startup")
def on_startup():
    # initialize DB client and db, keep client for shutdown
    client, db = get_db()
    app.state.db_client = client
    app.state.db = db
    app.state._scheduler_thread = run_scheduler(app.state.db)


@app.on_event("shutdown")
def on_shutdown():
    # close MongoDB client if present
    client = getattr(app.state, "db_client", None)
    if client:
        try:
            client.close()
        except Exception:
            pass