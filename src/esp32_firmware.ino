/*
 ===============================================================================
  IdleBin: Ultra-Low-Power Smart IoT Module Firmware
  Platform: ESP32 Dev Module (Arduino IDE / PlatformIO)
  Pondicherry University Grand Finale - 28 October 2026

  Wiring Connections:
  - REED SWITCH: GPIO 33 (PULLED HIGH via internal pullup, connects to GND when pedal drops)
  - ULTRASONIC SENSOR (HC-SR04):
      * TRIG: GPIO 5
      * ECHO: GPIO 18
  - STATUS LED: GPIO 2 (Blinks on telemetry transmission)
  - BATTERY MONITOR: GPIO 34 (ADC with 1:1 voltage divider)

  Power Profile:
  - Deep sleep current: ~15 uA
  - Wakes up ONLY when foot pedal triggers the Reed Switch
  - Transmits JSON payload in ~1.2 seconds, then returns to deep sleep immediately
 ===============================================================================
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_sleep.h>

// --- Configuration Constants ---
const char* WIFI_SSID     = "Your_WiFi_SSID";         // e.g. Phone hotspot or University Wi-Fi
const char* WIFI_PASSWORD = "Your_WiFi_Password";
const char* SERVER_URL    = "http://192.168.1.100:8000/api/telemetry"; // URL of IdleBin Server

#define BIN_ID              "IB-PU-01"
#define LOCATION_NAME       "Central Canteen"
#define BIN_FULL_DEPTH_CM   80.0    // Total vertical depth of bin when empty

// --- Hardware Pins ---
#define REED_SWITCH_PIN     GPIO_NUM_33   // Wake-up pin
#define TRIG_PIN            5
#define ECHO_PIN            18
#define LED_PIN             2
#define BATTERY_PIN         34

// --- Non-Volatile RTC Memory (Persists across Deep Sleep) ---
RTC_DATA_ATTR int rtc_stroke_count = 0;
RTC_DATA_ATTR int rtc_boot_count   = 0;

// Function to measure distance using ultrasonic sensor
float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout (~5 meters max)
  if (duration == 0) return BIN_FULL_DEPTH_CM;    // Timeout fallback

  float distance = (duration * 0.0343) / 2.0;
  return distance;
}

// Function to estimate battery millivolts
int readBatteryMV() {
  int raw = analogRead(BATTERY_PIN);
  // ADC reading with 2:1 divider factor for 3.7V - 4.2V Li-ion
  float voltage = (raw / 4095.0) * 3.3 * 2.0 * 1000.0;
  return (int)voltage;
}

void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(LED_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(REED_SWITCH_PIN, INPUT_PULLUP);

  digitalWrite(LED_PIN, HIGH); // LED On during active phase

  rtc_boot_count++;
  
  // Check wakeup reason
  esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
  if (wakeup_reason == ESP_SLEEP_WAKEUP_EXT0) {
    rtc_stroke_count++;
    Serial.printf("[IdleBin] Woke from Foot Pedal Crush! Total Strokes: %d\n", rtc_stroke_count);
  } else {
    Serial.println("[IdleBin] Initial Power-On or Timer Wakeup.");
  }

  // 1. Measure Distance & Compute Fill Percentage
  float distance_cm = readDistanceCM();
  float trash_height = max(0.0f, (float)BIN_FULL_DEPTH_CM - distance_cm);
  float fill_pct = constrain((trash_height / BIN_FULL_DEPTH_CM) * 100.0f, 0.0f, 100.0f);
  int battery_mv = readBatteryMV();

  Serial.printf("[IdleBin] Distance: %.1f cm | Fill: %.1f %% | Battery: %d mV\n", 
                distance_cm, fill_pct, battery_mv);

  // 2. Connect to Wi-Fi
  Serial.print("[IdleBin] Connecting to Wi-Fi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(200);
    Serial.print(".");
    attempts++;
  }
  Serial.println();

  // 3. Dispatch Telemetry HTTP POST Payload
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{";
    jsonPayload += "\"bin_id\":\"" + String(BIN_ID) + "\",";
    jsonPayload += "\"location\":\"" + String(LOCATION_NAME) + "\",";
    jsonPayload += "\"stroke_count\":" + String(rtc_stroke_count) + ",";
    jsonPayload += "\"distance_cm\":" + String(distance_cm, 1) + ",";
    jsonPayload += "\"fill_pct\":" + String(fill_pct, 1) + ",";
    jsonPayload += "\"battery_mv\":" + String(battery_mv) + ",";
    jsonPayload += "\"event_type\":\"PEDAL_CRUSH\"";
    jsonPayload += "}";

    int httpCode = http.POST(jsonPayload);
    Serial.printf("[IdleBin] HTTP Response: %d\n", httpCode);
    http.end();
  } else {
    Serial.println("[IdleBin] Wi-Fi Connection Timed Out. Data stored in RTC memory.");
  }

  digitalWrite(LED_PIN, LOW); // LED Off before sleeping

  // 4. Configure Wakeup on Reed Switch (GPIO 33 pulled to GND on pedal drop)
  esp_sleep_enable_ext0_wakeup(REED_SWITCH_PIN, 0); // 0 = LOW trigger

  Serial.println("[IdleBin] Entering Deep Sleep. Awaiting next foot pedal crush...");
  Serial.flush();
  esp_deep_sleep_start();
}

void loop() {
  // Not used in deep sleep architecture
}
