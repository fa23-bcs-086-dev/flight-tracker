from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FlightCreate(BaseModel):
    airline: str
    from_code: str = Field(..., alias="from")
    to_code: str = Field(..., alias="to")
    flightDate: datetime
    trackingStart: datetime
    trackingIntervalMinutes: Optional[int] = 10080

    model_config = {"populate_by_name": True}


class FlightOut(BaseModel):
    id: str
    airline: str
    from_code: str = Field(..., alias="from")
    to_code: str = Field(..., alias="to")
    flightDate: datetime
    trackingStart: datetime
    trackingIntervalMinutes: int
    active: bool
    createdAt: datetime

    model_config = {"populate_by_name": True}


class PricePointCreate(BaseModel):
    priceUSD: float
    timestamp: Optional[datetime] = None
    source: Optional[str] = "simulator"


class PricePointOut(BaseModel):
    id: str
    flight: str
    timestamp: datetime
    priceUSD: float
    source: str