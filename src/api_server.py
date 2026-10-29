"""
IdleBin REST Telemetry Server
FastAPI endpoint receiving live HTTP POST telemetry from ESP32 Microcontrollers
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn
from data_manager import DataManager

app = FastAPI(title="IdleBin Municipal IoT Gateway", version="1.0.0")


class TelemetryPacket(BaseModel):
    bin_id: str
    location: Optional[str] = "Ramapuram Municipal Sector"
    stroke_count: int
    distance_cm: float
    fill_pct: float
    battery_mv: Optional[int] = 4000
    event_type: Optional[str] = "PEDAL_CRUSH"


@app.get("/")
def health_check():
    return {
        "status": "ONLINE",
        "service": "IdleBin Municipal Gateway",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/telemetry")
def receive_telemetry(packet: TelemetryPacket):
    """
    Ingests live sensor pulse from ESP32:
    - Increments / updates stroke count
    - Updates fill level & distance
    - Logs event for anomaly analysis
    """
    bins = DataManager.load_bins()
    target = None
    for b in bins:
        if b["id"] == packet.bin_id:
            target = b
            break

    if not target:
        # Register new bin if unknown
        target = {
            "id": packet.bin_id,
            "name": packet.location or f"Bin {packet.bin_id}",
            "lat": 12.0200,
            "lng": 79.8540,
            "fill_pct": packet.fill_pct,
            "distance_cm": packet.distance_cm,
            "strokes": packet.stroke_count,
            "battery_mv": packet.battery_mv,
            "last_updated": datetime.now().isoformat(),
            "zone": "General Campus",
            "status": "NORMAL"
        }
        bins.append(target)
    else:
        target["strokes"] = packet.stroke_count
        target["distance_cm"] = round(packet.distance_cm, 1)
        target["fill_pct"] = round(packet.fill_pct, 1)
        target["battery_mv"] = packet.battery_mv
        target["last_updated"] = datetime.now().isoformat()

    if target["fill_pct"] >= 85.0:
        target["status"] = "CRITICAL"
    elif target["fill_pct"] >= 65.0:
        target["status"] = "WARNING"
    else:
        target["status"] = "NORMAL"

    DataManager.save_bins(bins)
    DataManager.log_telemetry_event({
        "bin_id": packet.bin_id,
        "event": packet.event_type,
        "stroke_count": packet.stroke_count,
        "fill_pct": packet.fill_pct,
        "distance_cm": packet.distance_cm,
        "timestamp": target["last_updated"]
    })

    return {
        "status": "SUCCESS",
        "bin_id": packet.bin_id,
        "updated_fill_pct": target["fill_pct"],
        "server_time": target["last_updated"]
    }


if __name__ == "__main__":
    print("Starting IdleBin Telemetry Gateway on http://0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
