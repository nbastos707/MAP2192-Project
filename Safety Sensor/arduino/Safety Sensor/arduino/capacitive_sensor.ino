/*
 * CAPACITIVE TOUCH SAFETY SENSOR - Data Collection
 * MAP2192 Data Science Project
 *
 * PURPOSE: Collect labeled sensor data for ML classification
 * OUTPUT: CSV format via Serial (timestamp, sensor_value, label)
 *
 * CIRCUIT:
 *   - Pin 4 (SEND) ---[1M Resistor]---+--- Pin 2 (RECEIVE)
 *                                     |
 *                              [Conductive Surface]
 *                                     |
 *                                    GND (optional)
 *
 *   - Pin 7 --- Button --- GND (for labeling data)
 *   - Pin 13 --- LED (built-in, for feedback)
 */

// ============================================================
// LIBRARY
// ============================================================
#include <CapacitiveSensor.h>

// ============================================================
// PIN DEFINITIONS
// ============================================================
const int SEND_PIN = 4;
const int RECEIVE_PIN = 2;
const int BUTTON_PIN = 7;
const int LED_PIN = 13;

// ============================================================
// SENSOR SETUP
// ============================================================
CapacitiveSensor sensor = CapacitiveSensor(SEND_PIN, RECEIVE_PIN);

// ============================================================
// VARIABLES
// ============================================================
int currentLabel = 0;          // 0 = safe, 1 = unsafe
unsigned long startTime;
int sampleCount = 0;

const long TOUCH_THRESHOLD = 100;

// ============================================================
// SETUP
// ============================================================
void setup() {
  Serial.begin(9600);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);

  // Turn off autocalibrate for consistent readings
  sensor.set_CS_AutocaL_Millis(0xFFFFFFFF);

  startTime = millis();

  Serial.println("timestamp,sensor_value,label");

  blinkLED(3);
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
  // Read the capacitive sensor (30 samples averaged)
  long sensorValue = sensor.capacitiveSensor(30);

  // Check button for label toggle
  if (digitalRead(BUTTON_PIN) == LOW) {
    currentLabel = 1 - currentLabel;
    digitalWrite(LED_PIN, currentLabel);

    // Debounce
    while (digitalRead(BUTTON_PIN) == LOW) {
      delay(10);
    }
    delay(200);
  }

  // Output CSV: timestamp,sensor_value,label
  unsigned long timestamp = millis() - startTime;
  Serial.print(timestamp);
  Serial.print(",");
  Serial.print(sensorValue);
  Serial.print(",");
  Serial.println(currentLabel);

  sampleCount++;

  // Basic threshold feedback
  if (sensorValue > TOUCH_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);
  } else if (currentLabel == 0) {
    digitalWrite(LED_PIN, LOW);
  }

  // 50ms = 20 samples per second
  delay(50);
}

// ============================================================
// HELPER FUNCTIONS
// ============================================================

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}
