# IdleBin Municipal Edge Telemetry Specification
**Document ID**: `SPEC-IB-TEL-2026-V1`  
**Target Architecture**: ESP32 Edge Sensor Node & Municipal ULB Cloud Gateway  
**Author**: IdleBin Engineering Fleet  

---

## 1. System Overview

IdleBin combines human-powered mechanical volume compaction with an autonomous IoT telemetry stack. This specification defines the physical sensing parameters, edge power duty cycles, outlier filtering thresholds, and data payload contracts between field-deployed smart bins and the municipal dispatch gateway.

---

## 2. Sensor Geometry & Transducer Calibration

The primary fill-level measurement is performed by a weather-sealed ultrasonic transducer (JSN-SR04T or waterproofed HC-SR04 variant) mounted in the bin collar:

| Parameter | Specification | Engineering Rationale |
| :--- | :--- | :--- |
| **Transducer Model** | JSN-SR04T-2.0 Waterproof Ultrasonic | Resistant to high humidity, municipal leachate fumes, and splash |
| **Bin Cavity Height ($H_{tot}$)** | $80.0\text{ cm}$ | Standard civilian 120L high-density polyethylene (HDPE) shell |
| **Collar Sensor Offset ($D_{offset}$)** | $5.0\text{ cm}$ | Deadband compensation preventing transducer blind-spot clipping ($<20\text{ cm}$) |
| **Effective Sensing Depth ($H_{eff}$)** | $75.0\text{ cm}$ | $H_{tot} - D_{offset}$ |
| **Measurement Beam Angle** | $\approx 45^\circ$ cone | Encompasses central compaction platen zone |
| **Outlier Deviation Threshold** | $\pm 25.0\text{ cm}$ | Hampel filter boundary to reject transient plastic bottle bounce reflections |

### 2.1 Fill Percentage Transfer Function

The calibrated fill level is calculated from the filtered distance $D_{filt}$:

$$\text{Fill Level (\%)} = \max\left(0.0, \min\left(100.0, \frac{H_{eff} - \max(0, D_{filt} - D_{offset})}{H_{eff}} \times 100.0\right)\right)$$

---

## 3. Edge Power Management & Sleep Schedule

To guarantee 180+ days of untethered operation on a single 3000mAh 18650 Li-ion cell:

- **Daytime Duty Cycle (06:00 - 22:00 IST)**: ESP32 deep sleep with timer wake every **15 minutes**.
- **Nighttime Duty Cycle (22:00 - 06:00 IST)**: Deep sleep extended to **60 minutes**.
- **Interrupt Wake (External RTC GPIO)**: Triggered immediately when a civilian presses the foot pedal (reed switch or mechanical microswitch contact on pedal lever), logging stroke count delta without waiting for timer expiration.

### 3.1 Battery ADC Telemetry Mapping

| Voltage Range ($V_{bat}$) | Battery Health State | Gateway Action |
| :--- | :--- | :--- |
| $> 3900\text{ mV}$ | **Optimal (100% - 85%)** | Normal 15-min reporting cycle |
| $3650\text{ mV} - 3900\text{ mV}$ | **Nominal (85% - 40%)** | Normal operation |
| $3400\text{ mV} - 3650\text{ mV}$ | **Low Battery (< 25%)** | Throttled transmission; field battery replacement ticket generated |
| $< 3400\text{ mV}$ | **Critical Cutoff** | Safe sleep to avoid deep Li-ion cell degradation |

---

## 4. Gateway REST Ingestion Schema

The edge node delivers compressed telemetry via standard HTTP POST over Wi-Fi / 4G LTE-M:

### Endpoint: `POST /api/telemetry`
**Headers**: `Content-Type: application/json`, `X-IdleBin-Node-Key: <HMAC_TOKEN>`

```json
{
  "bin_id": "IB-RAM-01",
  "location": "Easwari College Campus",
  "stroke_count": 412,
  "distance_cm": 11.2,
  "fill_pct": 86.0,
  "battery_mv": 4050,
  "event_type": "PEDAL_CRUSH"
}
```

### Response Schema (`200 OK`)
```json
{
  "status": "SUCCESS",
  "bin_id": "IB-RAM-01",
  "updated_fill_pct": 86.0,
  "server_time": "2026-11-04T20:15:40.128456"
}
```

---

## 5. Binary LoRaWAN Compact Frame (Optional Low-Bandwidth Link)

For municipal areas without cellular coverage, the node packs state into a 12-byte binary frame:

| Byte Offset | Field Name | Type | Scaling / Unit |
| :--- | :--- | :--- | :--- |
| `0x00 - 0x03` | Node ID Hash | `uint32_t` | FNV-1a Hash of `bin_id` |
| `0x04 - 0x05` | Stroke Counter | `uint16_t` | Cumulative pedal compressions |
| `0x06 - 0x07` | Raw Distance | `uint16_t` | Millimeters ($D_{cm} \times 10$) |
| `0x08` | Fill Level | `uint8_t` | $0 - 100\%$ |
| `0x09 - 0x0A` | Battery Voltage | `uint16_t` | Millivolts ($mV$) |
| `0x0B` | Status Flags | `uint8_t` | Bit 0: Jam Flag, Bit 1: Outlier Spike, Bit 2: Door Open |
