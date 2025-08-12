#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>
#include <ModbusMaster.h>

// WiFi Credentials
const char* ssid = "SEED-IOT-LAB";
const char* password = "SeEdLaB4303";

// Server endpoints - Updated to current IP address
const char* serverUrl = "http://192.168.0.102:8000/soil-data";       // POST sensor data
const char* relayControlUrl = "http://192.168.0.102:8000/relay-status"; // GET relay control

// Modbus & RS485 setup
#define MAX485_DE_RE 14
SoftwareSerial modbusSerial(13, 12); 
ModbusMaster node;

// Relay pin
#define RELAY_PIN 5  // D1 on NodeMCU

// Thresholds
#define HUMIDITY_THRESHOLD 25.0  // % — below this, relay turns ON automatically

// Mode & state tracking
String controlMode = "auto";  // "auto" or "manual"
bool relayState = false;

WiFiClient client;

void preTransmission() { digitalWrite(MAX485_DE_RE, HIGH); }
void postTransmission() { digitalWrite(MAX485_DE_RE, LOW); }

void setRelay(bool state) {
  relayState = state;
  // Inverted logic: LOW = ON, HIGH = OFF (common for relay modules)
  digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  Serial.println(state ? "⚡ Relay ON (GPIO LOW)" : "⛔ Relay OFF (GPIO HIGH)");
}

void setup() {
  Serial.begin(115200);
  modbusSerial.begin(9600);
  node.begin(1, modbusSerial);
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);

  pinMode(MAX485_DE_RE, OUTPUT);
  digitalWrite(MAX485_DE_RE, LOW);

  pinMode(RELAY_PIN, OUTPUT);
  setRelay(false); // Start OFF

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
  Serial.println("🎛️ Relay control enabled on GPIO5 (D1)");
}

void loop() {
  uint8_t result;
  uint16_t N = 255, P = 255, K = 255, PH = 255, EC = 255, HUM = 255, TMP = 255;

  result = node.readHoldingRegisters(0x001F, 1); if (result == node.ku8MBSuccess) N = node.getResponseBuffer(0);
  result = node.readHoldingRegisters(0x001E, 1); if (result == node.ku8MBSuccess) P = node.getResponseBuffer(0);
  result = node.readHoldingRegisters(0x0020, 1); if (result == node.ku8MBSuccess) K = node.getResponseBuffer(0);
  result = node.readHoldingRegisters(0x0006, 1); if (result == node.ku8MBSuccess) PH = node.getResponseBuffer(0);
  result = node.readHoldingRegisters(0x0015, 1); if (result == node.ku8MBSuccess) EC = node.getResponseBuffer(0);
  result = node.readHoldingRegisters(0x0012, 1); if (result == node.ku8MBSuccess) HUM = node.getResponseBuffer(0);
  
  // Try different temperature registers - most soil sensors use 0x0014
  result = node.readHoldingRegisters(0x0014, 1); if (result == node.ku8MBSuccess) TMP = node.getResponseBuffer(0);

  float humidityPercent = HUM / 10.0;

  // 🌱 Print sensor values to Serial Monitor
  Serial.println("---- Soil Sensor Readings ----");
  Serial.println("Nitrogen (N): " + String(N));
  Serial.println("Phosphorus (P): " + String(P));
  Serial.println("Potassium (K): " + String(K));
  Serial.println("pH: " + String(PH / 100.0));
  Serial.println("EC: " + String(EC));
  Serial.println("Humidity: " + String(humidityPercent) + " %");
  Serial.println("Temperature: " + String(TMP / 10.0) + " °C");
  Serial.println("Mode: " + controlMode);
  Serial.println("Relay: " + String(relayState ? "ON" : "OFF"));
  Serial.println("------------------------------");

  if (WiFi.status() == WL_CONNECTED) {
    // --- Send sensor data ---
    HTTPClient http;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String payload = "{";
    payload += "\"nitrogen\":" + String(N) + ",";
    payload += "\"phosphorus\":" + String(P) + ",";
    payload += "\"potassium\":" + String(K) + ",";
    payload += "\"ph\":" + String(PH / 100.0) + ",";
    payload += "\"ec\":" + String(EC) + ",";
    payload += "\"humidity\":" + String(humidityPercent) + ",";
    payload += "\"temperature\":" + String(TMP / 10.0) + ",";
    payload += "\"relay\":\"" + String(relayState ? "ON" : "OFF") + "\"";  // Fixed to match server expectation
    payload += "}";

    int httpCode = http.POST(payload);
    Serial.println("🌐 HTTP POST sent: Code " + String(httpCode));
    http.end();

    // --- Get control command from server ---
    HTTPClient httpRelay;
    httpRelay.begin(client, relayControlUrl);
    int httpCodeRelay = httpRelay.GET();
    if (httpCodeRelay == 200) {
      String relayResponse = httpRelay.getString();
      Serial.println("🔄 Server control response: " + relayResponse);

      // Check if mode command is present
      if (relayResponse.indexOf("manual") != -1) {
        controlMode = "manual";
        // If in manual mode, follow direct relay command
        if (relayResponse.indexOf("on") != -1 && !relayState) {
          setRelay(true);
          Serial.println("🎛️ Manual ON command executed");
        } else if (relayResponse.indexOf("off") != -1 && relayState) {
          setRelay(false);
          Serial.println("🎛️ Manual OFF command executed");
        }
      } else if (relayResponse.indexOf("auto") != -1) {
        controlMode = "auto";
        Serial.println("🤖 Switched to AUTO mode");
      }
    } else {
      Serial.println("⚠️ Failed to get relay status from server");
    }
    httpRelay.end();

    // --- Automatic control if in auto mode ---
    if (controlMode == "auto") {
      if (humidityPercent < HUMIDITY_THRESHOLD && !relayState) {
        setRelay(true);
        Serial.println("🤖 AUTO ON - Low moisture: " + String(humidityPercent) + "%");
      } else if (humidityPercent >= (HUMIDITY_THRESHOLD + 10) && relayState) {
        setRelay(false);
        Serial.println("🤖 AUTO OFF - Sufficient moisture: " + String(humidityPercent) + "%");
      }
    }

  } else {
    Serial.println("⚠️ WiFi not connected!");
  }

  delay(5000);  // Wait 5 seconds
}