"""
IdleBin Data & Telemetry Manager (Civilian Municipal Edition)
State Management, Historical Log Generation, and ESP32 Telemetry Ingestion
Puducherry Urban Local Body (ULB) Civilian Sector
"""

import json
import os
import random
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(__file__), "bins_state.json")
TELEMETRY_LOG_FILE = os.path.join(os.path.dirname(__file__), "telemetry_log.json")

INITIAL_CIVILIAN_BINS = [
    {
        "id": "IB-RAM-01",
        "name": "Easwari College Campus",
        "lat": 13.0310,
        "lng": 80.1810,
        "fill_pct": 86.0,
        "distance_cm": 11.2,
        "strokes": 410,
        "battery_mv": 4050,
        "last_updated": datetime.now().isoformat(),
        "zone": "Academic Core (High Bottle Discard)",
        "status": "CRITICAL"
    },
    {
        "id": "IB-RAM-02",
        "name": "DLF Cybercity Gate",
        "lat": 13.0335,
        "lng": 80.1780,
        "fill_pct": 91.0,
        "distance_cm": 7.2,
        "strokes": 520,
        "battery_mv": 3980,
        "last_updated": (datetime.now() - timedelta(minutes=4)).isoformat(),
        "zone": "IT Corporate Hub (Peak Can/Bottle Load)",
        "status": "CRITICAL"
    },
    {
        "id": "IB-RAM-03",
        "name": "Ramapuram Main Market",
        "lat": 13.0350,
        "lng": 80.1845,
        "fill_pct": 78.0,
        "distance_cm": 17.6,
        "strokes": 340,
        "battery_mv": 4120,
        "last_updated": (datetime.now() - timedelta(minutes=18)).isoformat(),
        "zone": "Commercial Retail Corridor",
        "status": "WARNING"
    },
    {
        "id": "IB-RAM-04",
        "name": "Mount-Poonamallee Junction",
        "lat": 13.0290,
        "lng": 80.1750,
        "fill_pct": 83.0,
        "distance_cm": 13.6,
        "strokes": 390,
        "battery_mv": 3910,
        "last_updated": (datetime.now() - timedelta(minutes=2)).isoformat(),
        "zone": "Transit Arterial Corridor",
        "status": "WARNING"
    },
    {
        "id": "IB-RAM-05",
        "name": "Manapakkam L&T Corridor",
        "lat": 13.0240,
        "lng": 80.1890,
        "fill_pct": 42.0,
        "distance_cm": 46.4,
        "strokes": 110,
        "battery_mv": 4170,
        "last_updated": (datetime.now() - timedelta(minutes=35)).isoformat(),
        "zone": "Residential & Tech Fringe",
        "status": "NORMAL"
    }
]


class DataManager:
    @classmethod
    def load_bins(cls):
        """Loads bins from JSON file or initializes default values."""
        if not os.path.exists(DATA_FILE):
            cls.save_bins(INITIAL_CIVILIAN_BINS)
            return INITIAL_CIVILIAN_BINS
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Check if data is already civilian or old campus format
                if data and "IB-PU" in data[0].get("id", ""):
                    cls.save_bins(INITIAL_CIVILIAN_BINS)
                    return INITIAL_CIVILIAN_BINS
                return data
        except Exception:
            return INITIAL_CIVILIAN_BINS

    @classmethod
    def save_bins(cls, bins_list):
        """Saves bins to disk."""
        with open(DATA_FILE, "w") as f:
            json.dump(bins_list, f, indent=2)

    @classmethod
    def register_pedal_stroke(cls, bin_id: str, stroke_count: int = 1):
        """
        Simulates or applies a live foot press event on a specific bin.
        Decreases distance (compaction), increases fill_pct, increments stroke count.
        """
        bins = cls.load_bins()
        target = None
        for b in bins:
            if b["id"] == bin_id:
                target = b
                break

        if target:
            target["strokes"] += stroke_count
            target["fill_pct"] = min(100.0, round(target["fill_pct"] + (0.9 * stroke_count), 1))
            target["distance_cm"] = max(2.0, round(target["distance_cm"] - (0.7 * stroke_count), 1))
            target["last_updated"] = datetime.now().isoformat()
            
            if target["fill_pct"] >= 85.0:
                target["status"] = "CRITICAL"
            elif target["fill_pct"] >= 65.0:
                target["status"] = "WARNING"
            else:
                target["status"] = "NORMAL"

            cls.save_bins(bins)
            cls.log_telemetry_event({
                "bin_id": bin_id,
                "event": "PEDAL_CRUSH_STROKE",
                "stroke_delta": stroke_count,
                "total_strokes": target["strokes"],
                "fill_pct": target["fill_pct"],
                "distance_cm": target["distance_cm"],
                "timestamp": target["last_updated"]
            })
            return target
        return None

    @classmethod
    def empty_bin(cls, bin_id: str):
        """Simulates municipal collection / bin emptying."""
        bins = cls.load_bins()
        for b in bins:
            if b["id"] == bin_id:
                b["fill_pct"] = 0.0
                b["distance_cm"] = 80.0
                b["status"] = "NORMAL"
                b["last_updated"] = datetime.now().isoformat()
                break
        cls.save_bins(bins)

    @classmethod
    def log_telemetry_event(cls, event_dict):
        """Appends telemetry log event."""
        events = []
        if os.path.exists(TELEMETRY_LOG_FILE):
            try:
                with open(TELEMETRY_LOG_FILE, "r") as f:
                    events = json.load(f)
            except Exception:
                events = []
        events.append(event_dict)
        if len(events) > 500:
            events = events[-500:]
        with open(TELEMETRY_LOG_FILE, "w") as f:
            json.dump(events, f, indent=2)

    @classmethod
    def get_bin_historical_data(cls, bin_id: str):
        """
        Generates historical time-series data for a specific bin over the last 6 hours
        to feed the ML regression forecaster.
        """
        now = datetime.now()
        timestamps = [now - timedelta(minutes=15 * (24 - i)) for i in range(25)]
        
        bins = cls.load_bins()
        target = next((b for b in bins if b["id"] == bin_id), bins[0])
        current_fill = target["fill_pct"]
        
        base_fill = max(10.0, current_fill - 45.0)
        fill_levels = []
        for i in range(25):
            progress = (i / 24.0) ** 1.3
            noise = random.uniform(-1.2, 1.2) if i < 24 else 0.0
            fill = base_fill + progress * (current_fill - base_fill) + noise
            fill_levels.append(round(min(100.0, max(0.0, fill)), 1))
            
        return timestamps, fill_levels
