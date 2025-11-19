from fastapi import APIRouter

router = APIRouter()

# If old top-level routes.search exists, reuse its router.
try:
    from routes import search as legacy_search  # legacy location
    router = legacy_search.router
except Exception:
    # fallback stub
    @router.get("/search/ping")
    def ping():
        return {"status": "search route placeholder"}
    from fastapi import APIRouter

router = APIRouter()

# If old top-level routes.flights exists, reuse its router.
try:
    from routes import flights as legacy_flights  # legacy location
    # legacy module must expose `router`
    router = legacy_flights.router
except Exception:
    # fallback stub
    @router.get("/flights/ping")
    def ping():
        return {"status": "flights route placeholder"}