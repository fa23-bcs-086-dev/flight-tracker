import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.db.client import get_db
from app.models import flight_doc, pricepoint_doc
from app.core.config import settings


def _parse_dt(value: Any) -> datetime:
    if value is None:
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt)
                except Exception:
                    continue
    raise ValueError(f"Cannot parse datetime from: {value!r}")


def _load_seed_json() -> Dict[str, List[Dict]]:
    """
    Try to load JSON data from common filenames in project root.
    Returns a dict with keys 'flights' and 'pricepoints'.
    """
    candidates = [
        "flight_seed.json",
        "Flight_seed.json",
        "flightSeed.json",
        "flights_seed.json",
        "flight_seed.json",
        "flight_seed.JSON",
    ]
    root = Path.cwd()
    for name in candidates:
        p = root / name
        if p.exists():
            try:
                with p.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                # normalize shapes
                if isinstance(data, dict):
                    flights = data.get("flights") or data.get("FLIGHTS") or data.get("data") or []
                    pricepoints = data.get("pricepoints") or data.get("PRICEPOINTS") or data.get("price_points") or []
                    # If top-level dict contains flights object already, return
                    return {"flights": flights or [], "pricepoints": pricepoints or []}
                if isinstance(data, list):
                    # treat as list of flights
                    return {"flights": data, "pricepoints": []}
            except Exception as exc:
                print(f"Failed to parse {p}: {exc}")
                continue
    # no JSON found
    return {}


def _load_seed_module() -> Dict[str, List[Dict]]:
    """
    Fallback: attempt to import a Python seed module (old behavior).
    """
    import importlib

    names = ["Flight_seed", "flight_seed", "flights_seed", "flightseed", "FlightSeed", "flightSeed"]
    for name in names:
        try:
            mod = importlib.import_module(name)
            data = {"flights": [], "pricepoints": []}
            if hasattr(mod, "get_seed_data") and callable(mod.get_seed_data):
                sd = mod.get_seed_data()
                if isinstance(sd, dict):
                    data["flights"] = sd.get("flights", [])
                    data["pricepoints"] = sd.get("pricepoints", [])
            if hasattr(mod, "FLIGHTS"):
                data["flights"] = getattr(mod, "FLIGHTS")
            if hasattr(mod, "flights"):
                data["flights"] = getattr(mod, "flights")
            if hasattr(mod, "PRICEPOINTS"):
                data["pricepoints"] = getattr(mod, "PRICEPOINTS")
            if hasattr(mod, "pricepoints"):
                data["pricepoints"] = getattr(mod, "pricepoints")
            return data
        except ModuleNotFoundError:
            continue
    return {"flights": [], "pricepoints": []}


def run_seed(dry_run: bool = False):
    # try JSON first
    seed = _load_seed_json()
    if not seed:
        seed = _load_seed_module()
    flights_in = seed.get("flights", []) or []
    pricepoints_in = seed.get("pricepoints", []) or []

    client, db = get_db()
    print(f"Using database: {settings.DATABASE_NAME} @ {settings.MONGODB_URI}")

    if dry_run:
        print("Dry run enabled - collections will NOT be cleared or modified.")
    else:
        print("Clearing collections: flights, pricepoints")
        db.flights.delete_many({})
        db.pricepoints.delete_many({})

    inserted_flights = []
    for idx, f in enumerate(flights_in):
        airline = f.get("airline") or f.get("airlineName")
        from_code = f.get("from") or f.get("from_code") or f.get("origin")
        to_code = f.get("to") or f.get("to_code") or f.get("destination")
        flight_date = _parse_dt(f.get("flightDate") or f.get("flight_date") or f.get("flightDateISO"))
        tracking_start = _parse_dt(f.get("trackingStart") or f.get("tracking_start") or f.get("trackingStartISO"))
        tracking_interval = int(f.get("trackingIntervalMinutes", f.get("tracking_interval_minutes", 10080) or 10080))

        doc = flight_doc(
            airline=airline,
            from_code=from_code,
            to_code=to_code,
            flight_date=flight_date,
            tracking_start=tracking_start,
            tracking_interval_minutes=tracking_interval,
        )
        if dry_run:
            print(f"[DRY] Insert flight idx={idx} -> {doc}")
            inserted_flights.append(None)
            continue

        res = db.flights.insert_one(doc)
        inserted_flights.append(res.inserted_id)
        print(f"Inserted flight idx={idx} _id={res.inserted_id}")

        nested_pp = f.get("pricepoints") or f.get("PRICEPOINTS") or []
        for pp_idx, pp in enumerate(nested_pp):
            ts = _parse_dt(pp.get("timestamp") or pp.get("ts"))
            price = float(pp.get("priceUSD") or pp.get("price") or pp.get("price_usd"))
            source = pp.get("source", "seed")
            pp_doc = pricepoint_doc(flight_id=res.inserted_id, price_usd=price, timestamp=ts, source=source)
            if dry_run:
                print(f"[DRY]  - pricepoint idx={pp_idx} -> {pp_doc}")
            else:
                rpp = db.pricepoints.insert_one(pp_doc)
                print(f"  - Inserted pricepoint _id={rpp.inserted_id}")

    for idx, pp in enumerate(pricepoints_in):
        flight_ref = pp.get("flight_index")
        if flight_ref is None:
            flight_ref = pp.get("flight_ref") or pp.get("flight")
        fid = None
        if isinstance(flight_ref, int):
            if 0 <= flight_ref < len(inserted_flights):
                fid = inserted_flights[flight_ref]
        elif isinstance(flight_ref, str):
            try:
                from bson import ObjectId

                if ObjectId.is_valid(flight_ref):
                    fid = ObjectId(flight_ref)
            except Exception:
                fid = None

        if fid is None:
            print(f"Skipping pricepoint idx={idx}: could not resolve flight reference ({flight_ref})")
            continue

        ts = _parse_dt(pp.get("timestamp") or pp.get("ts"))
        price = float(pp.get("priceUSD") or pp.get("price") or pp.get("price_usd"))
        source = pp.get("source", "seed")
        pp_doc = pricepoint_doc(flight_id=fid, price_usd=price, timestamp=ts, source=source)
        if dry_run:
            print(f"[DRY] Insert top-level pricepoint idx={idx} -> {pp_doc}")
        else:
            rpp = db.pricepoints.insert_one(pp_doc)
            print(f"Inserted top-level pricepoint idx={idx} _id={rpp.inserted_id}")

    try:
        client.close()
    except Exception:
        pass

    print("Seeding finished.")


if __name__ == "__main__":
    dry = len(sys.argv) > 1 and sys.argv[1].lower() in ("dry", "--dry", "preview")
    run_seed(dry_run=dry)