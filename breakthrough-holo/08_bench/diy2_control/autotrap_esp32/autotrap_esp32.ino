// DIY-2a automatic trap tester: ESP32 side of autotrap.py (line protocol over USB serial, 115200 baud).
// UNTESTED ON HARDWARE. Bring up with the laser driver UNPOWERED first and check every pin with a multimeter.
//
//   "P <0-255>" -> laser analog power (ESP32 DAC on GPIO25, 0..3.3 V)   reply "P <code>"
//   "L <0|1>"   -> laser TTL enable on GPIO26                           reply "L <state>"
//   "T <ms>"    -> tapper solenoid pulse on GPIO27 (capped at 200 ms)    reply "T <ms>"
//   "I?"        -> interlock state from GPIO4                           reply "I 1" (closed = safe) or "I 0"
//
// SAFETY (mandatory):
//  * The hardware interlock (ELECTRONICS.md section 1) removes the laser driver's power when the lid opens. This
//    firmware is NOT a safety device; it only mirrors the interlock state and fails safe on top of it.
//  * Put a 10 k pull-down on the driver's TTL input (GPIO26 line): some cheap drivers LASE WHEN TTL FLOATS (R11 1.4),
//    e.g. while the ESP32 is resetting. Test the polarity at the lowest current with the beam in a dump.
//  * Laser off and power 0 whenever: the interlock opens, a reset happens, or no command arrives for 5 s while the
//    laser is enabled (host crashed).
//  * Driver analog inputs are often 0-5 V; the ESP32 DAC gives 0-3.3 V. Calibrate code -> mW at the trap plane with the
//    thermal meter (autotrap.py --power_cal). Do not add gain beyond the driver's rated input.
// Wiring: GPIO27 -> 100 R -> gate of a logic-level N-MOSFET (e.g. AO3400), 10 k gate pull-down, solenoid between +V and
// drain with a 1N4007 flyback diode across it. GPIO4 -> relay K1 auxiliary NO contact -> GND (INPUT_PULLUP).
// Written for the original ESP32 (DAC on GPIO25); the ESP32-S3 has no DAC.

const int DAC_PIN = 25, LASER_EN_PIN = 26, TAP_PIN = 27, INTERLOCK_PIN = 4;
const uint32_t WATCHDOG_MS = 5000, TAP_MAX_MS = 200;
uint32_t lastCmd = 0;
bool laserOn = false;
String line;

void laserOff() { digitalWrite(LASER_EN_PIN, LOW); dacWrite(DAC_PIN, 0); laserOn = false; }
bool interlockClosed() { return digitalRead(INTERLOCK_PIN) == LOW; }

void setup() {
  pinMode(LASER_EN_PIN, OUTPUT); pinMode(TAP_PIN, OUTPUT); pinMode(INTERLOCK_PIN, INPUT_PULLUP);
  digitalWrite(TAP_PIN, LOW);
  laserOff();
  Serial.begin(115200);
}

void handle(const String& c) {
  lastCmd = millis();
  if (c == "I?") { Serial.println(interlockClosed() ? "I 1" : "I 0"); return; }
  if (c.length() < 3) { Serial.println("E"); return; }
  long v = c.substring(2).toInt();
  switch (c[0]) {
    case 'P':
      v = constrain(v, 0, 255);
      if (!interlockClosed()) v = 0;
      dacWrite(DAC_PIN, v);
      Serial.printf("P %ld\n", v);
      break;
    case 'L':
      if (v && interlockClosed()) { digitalWrite(LASER_EN_PIN, HIGH); laserOn = true; } else { laserOff(); }
      Serial.printf("L %d\n", laserOn ? 1 : 0);
      break;
    case 'T':
      v = constrain(v, 0, (long)TAP_MAX_MS);
      digitalWrite(TAP_PIN, HIGH); delay(v); digitalWrite(TAP_PIN, LOW);
      Serial.printf("T %ld\n", v);
      break;
    default:
      Serial.println("E");
  }
}

void loop() {
  if (!interlockClosed() && laserOn) laserOff();                       // mirror the hardware interlock
  if (laserOn && millis() - lastCmd > WATCHDOG_MS) laserOff();          // host silent: fail safe
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { line.trim(); handle(line); line = ""; }
    else if (line.length() < 32) line += ch;
  }
}
