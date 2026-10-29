"""
IdleBin Smart Route Optimizer (Civilian Municipal Edition)
Dynamic Municipal Collection Vehicle Routing for Puducherry Urban Local Body (ULB)
Covering Commercial Hubs, Tourist Promenades, Transit Terminals, and Public Markets
"""

import math
import folium
import numpy as np


class RouteOptimizer:
    """
    Optimizes municipal solid waste collection routes across Puducherry Urban Civilian Wards.
    Compares fixed daily scheduled sweeps against dynamic on-demand dispatch.
    """

    # Ramapuram Sanitation Depot (Nesapakkam Hub)
    CAMPUS_DEPOT = {
        "id": "DEPOT",
        "name": "Ramapuram Sanitation Depot (Nesapakkam Hub)",
        "lat": 13.0370,
        "lng": 80.1900,
        "type": "Depot"
    }

    DEFAULT_BINS = [
        {
            "id": "IB-RAM-01",
            "name": "Easwari College Campus",
            "lat": 13.0310,
            "lng": 80.1810,
            "fill_pct": 86.0,
            "strokes": 410,
            "predicted_overflow_hrs": 1.1,
            "zone": "Academic Core (High Bottle Discard)"
        },
        {
            "id": "IB-RAM-02",
            "name": "DLF Cybercity Gate",
            "lat": 13.0335,
            "lng": 80.1780,
            "fill_pct": 91.0,
            "strokes": 520,
            "predicted_overflow_hrs": 0.8,
            "zone": "IT Corporate Hub (Peak Can/Bottle Load)"
        },
        {
            "id": "IB-RAM-03",
            "name": "Ramapuram Main Market",
            "lat": 13.0350,
            "lng": 80.1845,
            "fill_pct": 78.0,
            "strokes": 340,
            "predicted_overflow_hrs": 1.9,
            "zone": "Commercial Retail Corridor"
        },
        {
            "id": "IB-RAM-04",
            "name": "Mount-Poonamallee Junction",
            "lat": 13.0290,
            "lng": 80.1750,
            "fill_pct": 83.0,
            "strokes": 390,
            "predicted_overflow_hrs": 1.4,
            "zone": "Transit Arterial Corridor"
        },
        {
            "id": "IB-RAM-05",
            "name": "Manapakkam L&T Corridor",
            "lat": 13.0240,
            "lng": 80.1890,
            "fill_pct": 42.0,
            "strokes": 110,
            "predicted_overflow_hrs": 8.5,
            "zone": "Residential & Tech Fringe"
        }
    ]

    @staticmethod
    def haversine_distance_km(lat1, lon1, lat2, lon2):
        """Calculates great-circle distance between two GPS coordinates in kilometers."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @classmethod
    def solve_route(cls, bins_list: list, threshold_fill_pct: float = 75.0):
        """
        Solves two collection schemes:
        1. Fixed Schedule: Depot -> All bins in sequence -> Depot
        2. Dynamic Smart Route: Depot -> Only bins >= threshold_fill_pct -> Depot
        """
        depot = cls.CAMPUS_DEPOT

        # 1. Fixed route (all civilian bins)
        fixed_sequence = [depot] + bins_list + [depot]
        fixed_distance_km = 0.0
        for i in range(len(fixed_sequence) - 1):
            fixed_distance_km += cls.haversine_distance_km(
                fixed_sequence[i]["lat"], fixed_sequence[i]["lng"],
                fixed_sequence[i+1]["lat"], fixed_sequence[i+1]["lng"]
            )

        # 2. Dynamic route (bins exceeding threshold or overflow < 2 hrs)
        critical_bins = [
            b for b in bins_list 
            if b["fill_pct"] >= threshold_fill_pct or b.get("predicted_overflow_hrs", 99) <= 2.0
        ]

        if not critical_bins:
            dynamic_sequence = [depot]
            dynamic_distance_km = 0.0
        else:
            unvisited = critical_bins.copy()
            dynamic_sequence = [depot]
            curr_loc = depot
            dynamic_distance_km = 0.0

            while unvisited:
                nearest_bin = min(
                    unvisited,
                    key=lambda b: cls.haversine_distance_km(curr_loc["lat"], curr_loc["lng"], b["lat"], b["lng"])
                )
                dist = cls.haversine_distance_km(curr_loc["lat"], curr_loc["lng"], nearest_bin["lat"], nearest_bin["lng"])
                dynamic_distance_km += dist
                dynamic_sequence.append(nearest_bin)
                curr_loc = nearest_bin
                unvisited.remove(nearest_bin)

            # Return to municipal depot
            return_dist = cls.haversine_distance_km(curr_loc["lat"], curr_loc["lng"], depot["lat"], depot["lng"])
            dynamic_distance_km += return_dist
            dynamic_sequence.append(depot)

        distance_saved_km = max(0.0, fixed_distance_km - dynamic_distance_km)
        pct_savings = (distance_saved_km / fixed_distance_km * 100.0) if fixed_distance_km > 0 else 0.0
        diesel_saved_l = distance_saved_km * 0.35
        inr_saved = diesel_saved_l * 94.0

        return {
            "fixed_distance_km": round(fixed_distance_km, 2),
            "dynamic_distance_km": round(dynamic_distance_km, 2),
            "distance_saved_km": round(distance_saved_km, 2),
            "pct_savings": round(pct_savings, 1),
            "diesel_saved_l": round(diesel_saved_l, 2),
            "inr_saved": round(inr_saved, 1),
            "fixed_stops_count": len(bins_list),
            "dynamic_stops_count": len(critical_bins),
            "fixed_sequence": fixed_sequence,
            "dynamic_sequence": dynamic_sequence,
            "critical_bins": critical_bins
        }

    @classmethod
    def generate_folium_map(cls, bins_list: list, route_data: dict, show_mode: str = "dynamic"):
        """
        Creates an interactive Folium map centered on the Puducherry Civilian Urban Zone.
        """
        center_lat = 11.9330
        center_lng = 79.8280

        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=14,
            tiles="OpenStreetMap"
        )

        # Mark Municipal Sanitation Depot
        folium.Marker(
            location=[cls.CAMPUS_DEPOT["lat"], cls.CAMPUS_DEPOT["lng"]],
            popup="<b>Puducherry Municipal Sanitation Depot</b> (Starting Depot)",
            tooltip="Municipal Depot",
            icon=folium.Icon(color="black", icon="building", prefix="fa")
        ).add_to(m)

        # Mark civilian bins
        for b in bins_list:
            fill = b["fill_pct"]
            if fill >= 80:
                color = "red"
                icon = "trash"
            elif fill >= 60:
                color = "orange"
                icon = "exclamation-triangle"
            else:
                color = "green"
                icon = "check-circle"

            html = f"""
            <div style="font-family: sans-serif; min-width: 180px;">
                <h4 style="margin: 0 0 5px 0; color: #1e3a8a;">{b['name']}</h4>
                <b>Ward / ID:</b> {b['id']}<br/>
                <b>Zone:</b> {b.get('zone', 'Civilian Area')}<br/>
                <b>Fill Level:</b> <span style="font-weight:bold; color:{'#dc2626' if fill>=80 else '#d97706' if fill>=60 else '#16a34a'}">{fill}%</span><br/>
                <b>Total Crushes:</b> {b['strokes']}<br/>
                <b>Est. Overflow:</b> {b.get('predicted_overflow_hrs', 'N/A')} hrs
            </div>
            """
            folium.Marker(
                location=[b["lat"], b["lng"]],
                popup=folium.Popup(html, max_width=260),
                tooltip=f"{b['name']} ({fill}%)",
                icon=folium.Icon(color=color, icon=icon, prefix="fa")
            ).add_to(m)

        # Draw routes
        if show_mode in ["dynamic", "both"] and len(route_data["dynamic_sequence"]) > 1:
            dyn_pts = [[pt["lat"], pt["lng"]] for pt in route_data["dynamic_sequence"]]
            folium.PolyLine(
                locations=dyn_pts,
                color="#2563eb",
                weight=5,
                opacity=0.85,
                dash_array="6, 6",
                tooltip=f"Dynamic Collection Route ({route_data['dynamic_distance_km']} km)"
            ).add_to(m)

        if show_mode in ["fixed", "both"]:
            fix_pts = [[pt["lat"], pt["lng"]] for pt in route_data["fixed_sequence"]]
            folium.PolyLine(
                locations=fix_pts,
                color="#94a3b8",
                weight=3,
                opacity=0.6,
                tooltip=f"Fixed Daily Sweep ({route_data['fixed_distance_km']} km)"
            ).add_to(m)

        return m
