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
// We use the CapacitiveSensor library which handles the timing
// Download: Sketch -> Include Library -> Manage Libraries -> "CapacitiveSensor"
#include <CapacitiveSensor.h>

// ============================================================
// PIN DEFINITIONS
// ============================================================
const int SEND_PIN = 4;        // Sends the charging signal
const int RECEIVE_PIN = 2;     // Measures the charge time
const int BUTTON_PIN = 7;      // Button to toggle labels
const int LED_PIN = 13;        // Visual feedback

// ============================================================
// SENSOR SETUP
// ============================================================
// CapacitiveSensor(sendPin, receivePin)
// The resistor (1M ohm) connects these two pins
// Higher resistor = more sensitive but slower
CapacitiveSensor sensor = CapacitiveSensor(SEND_PIN, RECEIVE_PIN);

// ============================================================
// VARIABLES
// ============================================================
int currentLabel = 0;          // 0 = safe, 1 = unsafe (toggle with button)
unsigned long startTime;       // For timestamps
int sampleCount = 0;           // Track number of samples

// Threshold for basic detection (we'll refine this with ML)
const long TOUCH_THRESHOLD = 100;

// ============================================================
// SETUP - Runs once at startup
// ============================================================
void setup() {
  // Start serial communication at 9600 baud
  // This sends data to your computer
  Serial.begin(9600);

  // Configure pins
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Button with internal pull-up
  pinMode(LED_PIN, OUTPUT);

  // Sensor configuration
  // Turn off autocalibrate for consistent readings
  sensor.set_CS_AutocaL_Millis(0xFFFFFFFF);

  // Record start time
  startTime = millis();

  // Print CSV header
  Serial.println("timestamp,sensor_value,label");

  // Visual confirmation
  blinkLED(3);
}

// ============================================================
// MAIN LOOP - Runs continuously
// ============================================================
void loop() {
  // ----------------------------------------------------------
  // STEP 1: Read the capacitive sensor
  // ----------------------------------------------------------
  // The parameter (30) is the number of samples to average
  // Higher = more stable but slower
  long sensorValue = sensor.capacitiveSensor(30);

  // ----------------------------------------------------------
  // STEP 2: Check button for label toggle
  // ----------------------------------------------------------
  if (digitalRead(BUTTON_PIN) == LOW) {
    // Button pressed - toggle label
    currentLabel = 1 - currentLabel;  // Flip between 0 and 1

    // Visual feedback: LED on = unsafe mode
    digitalWrite(LED_PIN, currentLabel);

    // Debounce - wait for button release
    while (digitalRead(BUTTON_PIN) == LOW) {
      delay(10);
    }
    delay(200);  // Extra debounce
  }

  // ----------------------------------------------------------
  // STEP 3: Output data in CSV format
  // ----------------------------------------------------------
  unsigned long timestamp = millis() - startTime;

  // Format: timestamp,sensor_value,label
  Serial.print(timestamp);
  Serial.print(",");
  Serial.print(sensorValue);
  Serial.print(",");
  Serial.println(currentLabel);

  sampleCount++;

  // ----------------------------------------------------------
  // STEP 4: Basic threshold feedback (before ML)
  // ----------------------------------------------------------
  // This gives immediate feedback while collecting data
  if (sensorValue > TOUCH_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);
  } else if (currentLabel == 0) {
    digitalWrite(LED_PIN, LOW);
  }

  // ----------------------------------------------------------
  // STEP 5: Sampling delay
  // ----------------------------------------------------------
  // 50ms = 20 samples per second
  // Adjust based on your needs
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
