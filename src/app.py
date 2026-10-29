"""
================================================================================
  IdleBin: Zero-Electricity Mechanical Compactor Dustbin & Smart Municipal Suite
  Civilian Urban Local Body (ULB) Edition - Puducherry Smart City & Municipal Wards
  Authored by AI Council of Engineering, IoT, MSW, Data Science & Competition Strategy
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_folium import st_folium
from datetime import datetime, timedelta

# Import IdleBin Modules
from physics_engine import PhysicsEngine
from ml_models import FillPredictor, JamAnomalyDetector, SwachhBharatImpact
from route_optimizer import RouteOptimizer
from data_manager import DataManager

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IdleBin | Civilian Smart Municipal Suite",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Clean Tech / Swachh Bharat UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .badge-critical {
        background-color: #fee2e2;
        color: #dc2626;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    .badge-warning {
        background-color: #fef3c7;
        color: #d97706;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
    .badge-normal {
        background-color: #dcfce7;
        color: #16a34a;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Header Section
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-title">♻️ IdleBin: Civilian Smart Municipal Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Zero-Electricity 4X Mechanical Plastic Compaction + Low-Cost IoT & ML Municipal Telemetry for Urban Wards</div>', unsafe_allow_html=True)
with col_h2:
    st.success("🏙️ **Civilian Sector**\nPuducherry Municipality (ULB)")

# -----------------------------------------------------------------------------
# AI Council Deliberation Expander
# -----------------------------------------------------------------------------
with st.expander("🏛️ View AI Council Deliberations & Civilian Architecture Decisions", expanded=False):
    st.markdown("""
    **The AI Council of Specialists** unified this system for high-density civilian municipal wards:
    * **Dr. Arvind Swaminathan (Mechanical Kinematics):** Proved Class-2 lever delivers **$>600\text{ N}$** force from body weight to permanently crease PET bottles past their 220 N yield limit.
    * **Dr. Priya Raman (IoT & Edge Systems):** Designed the ultra-low-power bolt-on clip (ESP32 in Deep Sleep + Reed Switch interrupt on foot pedal, enabling 6+ month battery life).
    * **Dr. Vikram Malhotra (Municipal Solid Waste & SBM-U 2.0):** Formulated the Blue Bin Dry-Recyclables separation for commercial bazars, beach promenades, and bus stands, eliminating the 80% trapped empty air that overflows Indian street dustbins in 2 hours.
    * **Dr. Elena Rostova (Data Science & ML):** Implemented polynomial time-to-overflow forecasting and jam anomaly detection.
    * **Prof. Karthik Sundaram (Jury Strategy):** Crafted the 2-minute live demo protocol for municipal stakeholders and grand finale judges.
    """)

# -----------------------------------------------------------------------------
# Global Data Load & Quick Stats
# -----------------------------------------------------------------------------
bins_data = DataManager.load_bins()
total_strokes = sum(b["strokes"] for b in bins_data)
impact = SwachhBharatImpact.calculate_impact(total_strokes, total_bins_deployed=len(bins_data))

# -----------------------------------------------------------------------------
# Main Navigation Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏢 Civilian Ward Monitor",
    "⚙️ Compaction Physics Simulator",
    "🧠 AI Predictive & Jam Analytics",
    "🗺️ Dynamic Route Optimizer",
    "🌱 Swachh Bharat Impact & ROI",
    "📡 IoT Hardware Bridge & ESP32"
])

# =============================================================================
# TAB 1: CIVILIAN WARD MONITOR
# =============================================================================
with tab1:
    st.subheader("🏢 Puducherry Municipality - Civilian Sector Ward Fleet")
    st.caption("Monitoring high-density public zones: Promenade Beach, Grand Bazaar, Bus Terminal, Shopping Districts, and Public Enclaves.")
    
    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Smart Bins", f"{len(bins_data)} Units", "6 Civilian Hotspots")
    with kpi2:
        avg_fill = np.mean([b["fill_pct"] for b in bins_data])
        st.metric("Sector Average Fill", f"{avg_fill:.1f}%", f"{sum(1 for b in bins_data if b['fill_pct'] >= 80)} Critical")
    with kpi3:
        st.metric("Total Civilian Crushes", f"{total_strokes:,}", "Mechanical Footsteps")
    with kpi4:
        st.metric("Plastic Bottles Crushed", f"{impact['bottles_crushed']:,}", "4X Air Volume Diverted")

    st.markdown("---")
    st.markdown("#### 📍 Real-Time Civilian Bin Status & Live Demonstration Controls")
    st.caption("Click **'Simulate Foot Pedal Crush'** on any bin to demonstrate how a citizen's footstep updates the sensor telemetry, stroke counter, and fill percentage instantly.")

    # Grid of Bin Cards
    cols = st.columns(3)
    for idx, b in enumerate(bins_data):
        with cols[idx % 3]:
            fill = b["fill_pct"]
            status = b.get("status", "NORMAL")
            badge_class = "badge-critical" if fill >= 85 else ("badge-warning" if fill >= 65 else "badge-normal")

            st.markdown(f"""
            <div class="metric-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <b style="font-size:1.05rem; color:#1e293b;">{b['id']}</b>
                    <span class="{badge_class}">{status}</span>
                </div>
                <div style="font-size:0.9rem; font-weight:600; color:#1e3a8a; margin-bottom:4px;">{b['name']}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-bottom:10px; height:24px;">{b.get('zone', 'Civilian Sector')}</div>
                <div style="font-size:1.8rem; font-weight:800; color:{'#dc2626' if fill>=85 else '#d97706' if fill>=65 else '#16a34a'};">
                    {fill}%
                </div>
                <div style="font-size:0.8rem; color:#64748b; margin-bottom:12px;">Fill Level ({b['distance_cm']} cm clearance)</div>
            </div>
            """, unsafe_allow_html=True)

            # Interactive Actions for Live Pitch
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button(f"🦶 Crush", key=f"crush_{b['id']}", help="Simulates citizen stepping on the foot pedal"):
                    DataManager.register_pedal_stroke(b["id"], stroke_count=1)
                    st.rerun()
            with btn_col2:
                if st.button(f"🧹 Empty", key=f"empty_{b['id']}", help="Simulates municipal collection"):
                    DataManager.empty_bin(b["id"])
                    st.rerun()

            st.caption(f"🔋 {b.get('battery_mv', 4000)} mV | 🔄 {b['strokes']} strokes")
            st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# TAB 2: COMPACTION PHYSICS SIMULATOR
# =============================================================================
with tab2:
    st.subheader("⚙️ Mechanical Physics & Lever Kinematics Simulator")
    st.markdown("""
    **Prove the ~600 N Force Claim with Lever Kinematics & PET Buckling Mechanics.**
    Judges and municipal engineers can adjust the sliders below to test how citizen body weights and lever arm ratios deliver crushing forces that permanently buckle plastic bottles.
    """)

    sim_col1, sim_col2 = st.columns([1, 1.3])

    with sim_col1:
        st.markdown("#### 🎛️ Input Physical Parameters")
        foot_weight = st.slider("Citizen Foot Downward Weight (kg)", min_value=30.0, max_value=100.0, value=50.0, step=1.0,
                                help="Typical human adult stepping firmly on the pedal")
        pedal_length = st.slider("Pedal Lever Arm Length L1 (cm)", min_value=25.0, max_value=55.0, value=38.0, step=1.0,
                                 help="Total length from pivot hinge to pedal footpad")
        pivot_offset = st.slider("Pushrod Distance from Pivot L2 (cm)", min_value=15.0, max_value=35.0, value=28.0, step=1.0,
                                 help="Offset where the vertical pushrod connects to the lever")
        platen_dia = st.slider("Platen Pressing Plate Diameter (cm)", min_value=15.0, max_value=35.0, value=24.0, step=1.0,
                               help="Diameter of the circular overhead crushing plate")

        kinematics = PhysicsEngine.calculate_kinematics(foot_weight, pedal_length, pivot_offset, platen_dia)

        st.markdown("---")
        st.markdown(f"**Mechanical Advantage (MA):** `{kinematics['mechanical_advantage']}x`")
        st.markdown(f"**Calculated Compaction Force:** `{kinematics['compaction_force_n']} N`")
        st.markdown(f"**Effective Pressure:** `{kinematics['pressure_kpa']} kPa` (`{kinematics['pressure_n_per_cm2']} N/cm²`)")
        st.markdown(f"**Compaction Ratio:** `{kinematics['compaction_ratio']}x` (Eliminates $\approx 75\%$ of trapped air)")

        if kinematics["exceeds_permanent"]:
            st.success(f"✅ **{kinematics['deformation_status']}**\nPlastic crystalline walls crease permanently. Rebound elasticity is only ~{kinematics['rebound_pct']}%.")
        elif kinematics["exceeds_yield"]:
            st.warning(f"⚠️ **{kinematics['deformation_status']}**\nPlastic buckles partially. Baffles and weight of upper layers hold it down.")
        else:
            st.error(f"❌ **{kinematics['deformation_status']}**\nInsufficient force to buckle thick PET walls.")

    with sim_col2:
        st.markdown("#### 📊 Force vs Body Weight Curve")
        weights, forces = PhysicsEngine.generate_force_weight_curve(pedal_length, pivot_offset)

        fig_physics = go.Figure()

        fig_physics.add_trace(go.Scatter(
            x=weights, y=forces,
            mode='lines+markers',
            name='Generated Compaction Force (N)',
            line=dict(color='#2563eb', width=3),
            marker=dict(size=6)
        ))

        fig_physics.add_trace(go.Scatter(
            x=[foot_weight], y=[kinematics['compaction_force_n']],
            mode='markers',
            name='Current Citizen Setting',
            marker=dict(color='#ef4444', size=14, symbol='star')
        ))

        fig_physics.add_hline(
            y=PhysicsEngine.PET_YIELD_FORCE_NEWTONS,
            line_dash="dash", line_color="#f59e0b",
            annotation_text="PET Buckling Yield Limit (~220 N)",
            annotation_position="bottom right"
        )

        fig_physics.add_hline(
            y=PhysicsEngine.PET_PERMANENT_DEFORM_FORCE,
            line_dash="dash", line_color="#10b981",
            annotation_text="Permanent Plastic Creasing (~450 N)",
            annotation_position="top right"
        )

        fig_physics.update_layout(
            title="Compaction Force Delivery vs User Weight",
            xaxis_title="Foot Step Weight (kg)",
            yaxis_title="Downward Force on Platen (Newtons)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=360
        )
        st.plotly_chart(fig_physics, width='stretch')

        st.info("""
        **Swachh Bharat Resilience:**
        1. **Zero Electronics in Compactor:** Unlike motorized smart bins that break when washed down by municipal cleaners, IdleBin uses pure mechanical leverage.
        2. **Bio-Filter False Bottom:** If tea or water is poured inside, liquid drains into an activated coconut charcoal tray that neutralizes odors.
        """)


# =============================================================================
# TAB 3: AI PREDICTIVE ANALYTICS & JAM DETECTION
# =============================================================================
with tab3:
    st.subheader("🧠 Machine Learning Fill Forecaster & Anomaly Detector")
    st.markdown("""
    Civilian Municipalities need **Predictive Foresight** to dispatch garbage tippers before bins overflow onto crowded pedestrian sidewalks.
    """)

    ai_col1, ai_col2 = st.columns([1, 1.2])

    with ai_col1:
        st.markdown("#### 🎯 Select Civilian Bin to Analyze")
        bin_options = {b["id"]: f"{b['id']} - {b['name']}" for b in bins_data}
        selected_bin_id = st.selectbox("Target Bin", options=list(bin_options.keys()), format_func=lambda x: bin_options[x])

        target_bin = next(b for b in bins_data if b["id"] == selected_bin_id)
        
        timestamps, fills = DataManager.get_bin_historical_data(selected_bin_id)
        predictor = FillPredictor(degree=2)
        forecast_result = predictor.fit_and_predict(timestamps, fills, forecast_hours=4.0)

        st.metric(
            "Current Fill Level",
            f"{target_bin['fill_pct']}%",
            f"{forecast_result['velocity_pct_per_hr']} % / hr fill rate"
        )
        
        overflow_hrs = forecast_result["time_to_overflow_hours"]
        if overflow_hrs < 2.0:
            st.error(f"🚨 **URGENT:** Predicted Overflow in **{overflow_hrs} hours** ({forecast_result['overflow_timestamp'].strftime('%I:%M %p')})")
        else:
            st.success(f"⏱️ **Normal:** Capacity safe for **{overflow_hrs} hours** ({forecast_result['overflow_timestamp'].strftime('%I:%M %p')})")

        st.markdown("---")
        st.markdown("#### 🔍 Mechanical Jam & Tamper Anomaly Detector")
        st.caption("Detects whether pedal strokes produce expected plastic compaction or indicate a platen jam / rigid obstruction (e.g., coconut shell or glass bottle).")

        test_strokes = st.number_input("Pedal Strokes Registered", min_value=0, max_value=10, value=3)
        test_fill_delta = st.slider("Measured Volume Compression (cm)", min_value=-3.0, max_value=8.0, value=0.2, step=0.1)

        anomaly = JamAnomalyDetector.analyze_event(test_strokes, test_fill_delta)
        if anomaly["severity"] == "CRITICAL":
            st.error(f"❌ **{anomaly['status']}**\n{anomaly['message']}")
        elif anomaly["severity"] == "WARNING":
            st.warning(f"⚠️ **{anomaly['status']}**\n{anomaly['message']}")
        else:
            st.success(f"✅ **{anomaly['status']}**\n{anomaly['message']}")

    with ai_col2:
        st.markdown("#### 📈 ML Time-Series Fill Forecast & Projection")

        fig_forecast = go.Figure()

        fig_forecast.add_trace(go.Scatter(
            x=timestamps, y=fills,
            mode='lines+markers',
            name='Historical Telemetry (Sensor)',
            line=dict(color='#0284c7', width=2),
            marker=dict(size=5)
        ))

        fig_forecast.add_trace(go.Scatter(
            x=forecast_result["forecast_timestamps"],
            y=forecast_result["forecast_fills"],
            mode='lines',
            name='ML Predicted Trajectory (Ridge Polynomial)',
            line=dict(color='#ef4444', width=3, dash='dash')
        ))

        fig_forecast.add_hline(
            y=100.0,
            line_dash="dot",
            line_color="#dc2626",
            annotation_text="Critical Overflow Limit (100%)",
            annotation_position="top left"
        )

        fig_forecast.add_hline(
            y=80.0,
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text="Early Dispatch Threshold (80%)",
            annotation_position="bottom left"
        )

        fig_forecast.update_layout(
            title=f"Predictive Fill Progression for {target_bin['name']}",
            xaxis_title="Time",
            yaxis_title="Fill Percentage (%)",
            yaxis=dict(range=[0, 110]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        st.plotly_chart(fig_forecast, width='stretch')

        st.caption(f"Model Quality: R² Score = {forecast_result['r2_score']} | Algorithm: 2nd Order Ridge Polynomial Regressor with Monotonic Velocity Clamping.")


# =============================================================================
# TAB 4: DYNAMIC ROUTE OPTIMIZER
# =============================================================================
with tab4:
    st.subheader("🗺️ Dynamic Municipal Collection Route Optimizer")
    st.markdown("""
    **Transforming Fixed Civilian Waste Routes into Demand-Driven Smart Routes.**
    Municipal tippers traditionally burn diesel visiting half-empty bins every morning.
    IdleBin dispatches trucks **only to bins that need collection**, optimizing the GPS path across Puducherry urban wards.
    """)

    route_col1, route_col2 = st.columns([1, 2])

    with route_col1:
        threshold = st.slider("Dispatch Threshold (% Fill)", min_value=50.0, max_value=90.0, value=75.0, step=5.0)
        route_mode = st.radio("Route Display Mode", ["Dynamic On-Demand Only", "Fixed Daily Sweep Only", "Compare Both"], index=2)
        mode_key = "dynamic" if "Dynamic" in route_mode else ("fixed" if "Fixed" in route_mode else "both")

        route_data = RouteOptimizer.solve_route(bins_data, threshold_fill_pct=threshold)

        st.markdown("---")
        st.markdown("#### 💰 Logistics Efficiency Comparison")
        st.metric("Fixed Sweep Distance", f"{route_data['fixed_distance_km']} km", f"{route_data['fixed_stops_count']} Civilian Bins")
        st.metric("Dynamic Smart Distance", f"{route_data['dynamic_distance_km']} km", f"{route_data['dynamic_stops_count']} Bins Needing Pickup")
        st.metric("Distance Saved", f"{route_data['distance_saved_km']} km", f"-{route_data['pct_savings']}% Route Reduction")
        st.metric("Diesel Saved per Run", f"{route_data['diesel_saved_l']} L", f"₹{route_data['inr_saved']:.0f} Saved per Run")

    with route_col2:
        st.markdown("#### 🗺️ Puducherry Urban Civilian Sector Collection Map")
        folium_map = RouteOptimizer.generate_folium_map(bins_data, route_data, show_mode=mode_key)
        st_folium(folium_map, width="100%", height=450)
        st.caption("Blue Dashed Path: Dynamic Smart Route | Grey Path: Fixed Daily Sweep | Red Markers: Critical Bins | Green: Low Fill")


# =============================================================================
# TAB 5: SWACHH BHARAT IMPACT & ROI
# =============================================================================
with tab5:
    st.subheader("🌱 Swachh Bharat Impact & Economic ROI Model")
    st.markdown("""
    **Why Municipalities & State Governments Choose IdleBin over Commercial Solar Bins.**
    """)

    imp_col1, imp_col2, imp_col3 = st.columns(3)
    with imp_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color:#1e3a8a; margin:0;">📦 4X Volume Cut</h3>
            <p style="font-size:2rem; font-weight:800; color:#0284c7; margin:5px 0;">{impact['volume_saved_liters']:,} L</p>
            <p style="color:#64748b; font-size:0.85rem;">Urban street volume saved by eliminating trapped air</p>
        </div>
        """, unsafe_allow_html=True)
    with imp_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color:#1e3a8a; margin:0;">🚛 Truck Trips Cut</h3>
            <p style="font-size:2rem; font-weight:800; color:#10b981; margin:5px 0;">{impact['truck_trips_saved']} Trips</p>
            <p style="color:#64748b; font-size:0.85rem;">Fewer municipal tipper trips required (50% reduction)</p>
        </div>
        """, unsafe_allow_html=True)
    with imp_col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color:#1e3a8a; margin:0;">🌍 Carbon Averted</h3>
            <p style="font-size:2rem; font-weight:800; color:#d97706; margin:5px 0;">{impact['co2_emissions_averted_kg']} kg</p>
            <p style="color:#64748b; font-size:0.85rem;">CO₂ emissions avoided from municipal collection trucks</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💵 Capital Expenditure Comparison (100 Bins City Deployment)")

    cost_df = pd.DataFrame({
        "System Type": ["Imported Solar Compactor Bin (e.g. Bigbelly)", "IdleBin Smart Municipal Unit (Ours)"],
        "Per-Unit Cost (INR)": [350000, 1550],
        "100 Bins Deployment (INR)": [35000000, 155000],
        "Maintenance & Motor Breakdowns": ["High (Motors, solar panels break in dust/rain)", "Zero (100% mechanical pedal, passive sensor)"],
        "Power Requirement": ["Solar battery & charging circuit", "Zero electricity for compaction; coin cell/18650 for IoT"]
    })
    st.table(cost_df)

    st.success(f"""
    💡 **Economic Bottom Line for Municipal Commissioners:**
    For the price of **JUST ONE** imported solar compactor bin (₹3,50,000), a municipal corporation can deploy **over 220 IdleBins**, permanently eliminating street overflowing across an entire urban zone!
    """)


# =============================================================================
# TAB 6: IOT HARDWARE BRIDGE & ESP32 CODE
# =============================================================================
with tab6:
    st.subheader("📡 IoT Hardware Integration & ESP32 Firmware")
    st.markdown("""
    The IdleBin Smart Module clips onto the mechanical bin without altering its zero-power physics.
    Use this tab to inspect the REST API payload or copy the complete Arduino C++ firmware sketch for flashing your ESP32.
    """)

    iot_col1, iot_col2 = st.columns([1, 1.2])

    with iot_col1:
        st.markdown("#### 🔌 Telemetry REST API Gateway")
        st.code("POST http://<server_ip>:8000/api/telemetry\nContent-Type: application/json", language="http")

        st.markdown("##### Sample JSON Telemetry Payload:")
        sample_json = {
            "bin_id": target_bin["id"],
            "location": target_bin["name"],
            "stroke_count": target_bin["strokes"] + 1,
            "distance_cm": target_bin["distance_cm"] - 1.2,
            "fill_pct": min(100.0, target_bin["fill_pct"] + 1.5),
            "battery_mv": 4050,
            "event_type": "PEDAL_CRUSH"
        }
        st.json(sample_json)

        if st.button("🚀 Send Mock ESP32 Pulse to Civilian Fleet"):
            DataManager.register_pedal_stroke(target_bin["id"], stroke_count=1)
            st.success(f"Telemetry pulse received from {target_bin['name']}! Bin fill and stroke counter updated.")
            st.rerun()

    with iot_col2:
        st.markdown("#### 💻 Complete ESP32 Arduino Firmware (`esp32_firmware.ino`)")
        try:
            with open("esp32_firmware.ino", "r") as f:
                code_content = f.read()
            st.code(code_content[:1800] + "\n\n// ... [Full code in esp32_firmware.ino] ...", language="cpp")
            st.download_button("📥 Download esp32_firmware.ino", data=code_content, file_name="esp32_firmware.ino", mime="text/plain")
        except Exception:
            st.info("Firmware file located in directory: `esp32_firmware.ino`")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#64748b; font-size:0.85rem;">
    IdleBin Civilian Municipal Innovation Project &bull; Puducherry Urban Local Body (ULB) &bull; Zero-Electricity Compaction
</div>
""", unsafe_allow_html=True)
