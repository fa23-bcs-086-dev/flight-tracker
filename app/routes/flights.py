from fastapi import APIRouter, Request, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app import models as app_models
from app.schemas import FlightCreate, FlightOut, PricePointCreate, PricePointOut

router = APIRouter()


def _oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")


def _serialize_flight(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "airline": doc.get("airline"),
        "from": doc.get("from"),
        "to": doc.get("to"),
        "flightDate": doc.get("flightDate"),
        "trackingStart": doc.get("trackingStart"),
        "trackingIntervalMinutes": doc.get("trackingIntervalMinutes"),
        "active": doc.get("active", True),
        "createdAt": doc.get("createdAt"),
    }


def _serialize_pricepoint(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "flight": str(doc.get("flight")),
        "timestamp": doc.get("timestamp"),
        "priceUSD": doc.get("priceUSD"),
        "source": doc.get("source"),
    }


@router.post("/flights", response_model=FlightOut, status_code=status.HTTP_201_CREATED)
def create_flight(payload: FlightCreate, request: Request):
    db = request.app.state.db
    doc = app_models.flight_doc(
        airline=payload.airline,
        from_code=payload.from_code,
        to_code=payload.to_code,
        flight_date=payload.flightDate,
        tracking_start=payload.trackingStart,
        tracking_interval_minutes=payload.trackingIntervalMinutes,
    )
    res = db.flights.insert_one(doc)
    created = db.flights.find_one({"_id": res.inserted_id})
    return _serialize_flight(created)


@router.get("/flights", response_model=List[FlightOut])
def list_flights(request: Request, limit: int = 50, skip: int = 0):
    db = request.app.state.db
    cursor = db.flights.find().skip(int(skip)).limit(int(limit))
    return [_serialize_flight(d) for d in cursor]


@router.get("/flights/{flight_id}", response_model=FlightOut)
def get_flight(flight_id: str, request: Request):
    db = request.app.state.db
    oid = _oid(flight_id)
    doc = db.flights.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Flight not found")
    return _serialize_flight(doc)


@router.post("/flights/{flight_id}/prices", response_model=PricePointOut, status_code=status.HTTP_201_CREATED)
def add_pricepoint(flight_id: str, payload: PricePointCreate, request: Request):
    db = request.app.state.db
    oid = _oid(flight_id)
    # ensure flight exists
    if not db.flights.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Flight not found")
    doc = app_models.pricepoint_doc(flight_id=oid, price_usd=payload.priceUSD, timestamp=payload.timestamp, source=payload.source)
    res = db.pricepoints.insert_one(doc)
    created = db.pricepoints.find_one({"_id": res.inserted_id})
    return _serialize_pricepoint(created)


@router.get("/flights/{flight_id}/prices", response_model=List[PricePointOut])
def list_pricepoints(flight_id: str, request: Request, limit: int = 100, sort_asc: bool = True):
    db = request.app.state.db
    oid = _oid(flight_id)
    if not db.flights.find_one({"_id": oid}):
        raise HTTPException(status_code=404, detail="Flight not found")
    sort_dir = 1 if sort_asc else -1
    cursor = db.pricepoints.find({"flight": oid}).sort("timestamp", sort_dir).limit(int(limit))
    return [_serialize_pricepoint(d) for d in cursor]