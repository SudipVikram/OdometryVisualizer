/* 
* Code for Punte Robot's visualizer on the ESP32 side
* code by Beyond Apogee, Nepal
* Author: Sudip Vikram Adhikari
*/

#include <BluetoothSerial.h>
BluetoothSerial SerialBT;

#define ENCODER_LEFT_A   13   // C1 Phase A left motor
#define ENCODER_LEFT_B   12   // C2 Phase B left motor
#define ENCODER_RIGHT_A  32   // C1 Phase A right motor
#define ENCODER_RIGHT_B  33   // C2 Phase B right motor

// Motor PWM pins
#define MOTOR_LEFT_IA    25
#define MOTOR_LEFT_IB    26
#define MOTOR_RIGHT_IA   27
#define MOTOR_RIGHT_IB   14

// ─── Left motor variables ────────────────────────────────────────
volatile int lastEncodedLeft = 0;
volatile long encoderLeft    = 0;

// ─── Right motor variables ───────────────────────────────────────
volatile int lastEncodedRight = 0;
volatile long encoderRight    = 0;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("Punte Robot");   // Bluetooth name

  pinMode(ENCODER_LEFT_A,  INPUT_PULLUP);
  pinMode(ENCODER_LEFT_B,  INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_A, INPUT_PULLUP);
  pinMode(ENCODER_RIGHT_B, INPUT_PULLUP);

  // Attach interrupts
  attachInterrupt(ENCODER_LEFT_A,  updateLeftEncoder,  CHANGE);
  attachInterrupt(ENCODER_LEFT_B,  updateLeftEncoder,  CHANGE);
  attachInterrupt(ENCODER_RIGHT_A, updateRightEncoder, CHANGE);
  attachInterrupt(ENCODER_RIGHT_B, updateRightEncoder, CHANGE);

  // Optional: set motor pins to LOW so motors don't spin at startup
  pinMode(MOTOR_LEFT_IA,  OUTPUT);
  pinMode(MOTOR_LEFT_IB,  OUTPUT);
  pinMode(MOTOR_RIGHT_IA, OUTPUT);
  pinMode(MOTOR_RIGHT_IB, OUTPUT);

  // set all the motors to low initially
  digitalWrite(MOTOR_LEFT_IA,  LOW);
  digitalWrite(MOTOR_LEFT_IB,  LOW);
  digitalWrite(MOTOR_RIGHT_IA, LOW);
  digitalWrite(MOTOR_RIGHT_IB, LOW);
}

void loop() {
  // Format that is easy to parse in Python / Pygame visualizer
  Serial.print("L:");
  Serial.print(encoderLeft);
  Serial.print(",R:");
  Serial.print(encoderRight);
  Serial.println();

  //delay(40);   // ≈25 Hz – reasonable compromise between responsiveness and serial load

  // ─── Send encoders every ~50 ms ────────────────────────
    static unsigned long t0 = 0;
    if (millis() - t0 >= 50) {
        t0 = millis();
        SerialBT.print("L:");
        SerialBT.print(encoderLeft);
        SerialBT.print(" R:");
        SerialBT.println(encoderRight);
    }

    // ─── Receive motor commands ────────────────────────────
    if (SerialBT.available()) {
        String cmd = SerialBT.readStringUntil('\n');
        cmd.trim();

        if (cmd == "FORWARD"){ /* both motors forward */ 
          digitalWrite(MOTOR_LEFT_IA, HIGH);
          digitalWrite(MOTOR_LEFT_IB, LOW);
          digitalWrite(MOTOR_RIGHT_IA, HIGH);
          digitalWrite(MOTOR_RIGHT_IB, LOW);
        } else if (cmd == "BACKWARD"){ /* both backward */ 
          digitalWrite(MOTOR_LEFT_IA, LOW);
          digitalWrite(MOTOR_LEFT_IB, HIGH);
          digitalWrite(MOTOR_RIGHT_IA, LOW);
          digitalWrite(MOTOR_RIGHT_IB, HIGH);
        } else if (cmd == "LEFT"){ /* move left */ 
          digitalWrite(MOTOR_LEFT_IA, LOW);
          digitalWrite(MOTOR_LEFT_IB, HIGH);
          digitalWrite(MOTOR_RIGHT_IA, HIGH);
          digitalWrite(MOTOR_RIGHT_IB, LOW);
        } else if (cmd == "RIGHT"){ /* move right */
          digitalWrite(MOTOR_LEFT_IA, HIGH);
          digitalWrite(MOTOR_LEFT_IB, LOW);
          digitalWrite(MOTOR_RIGHT_IA, LOW);
          digitalWrite(MOTOR_RIGHT_IB, HIGH); 
        } else if (cmd == "STOP"){ /* STOP */
          digitalWrite(MOTOR_LEFT_IA, LOW);
          digitalWrite(MOTOR_LEFT_IB, LOW);
          digitalWrite(MOTOR_RIGHT_IA, LOW);
          digitalWrite(MOTOR_RIGHT_IB, LOW);
        }
    }
}

// ─── Left motor interrupt handler ─────────────────────────────────
void updateLeftEncoder() {
  int current_MSB = digitalRead(ENCODER_LEFT_A);
  int current_LSB = digitalRead(ENCODER_LEFT_B);

  int current_state = 0;
  if (current_MSB == 1) current_state = 2;
  if (current_LSB == 1) current_state += 1;

  int transition = lastEncodedLeft * 4 + current_state;

  // Counter-clockwise detected
  if (transition == 13 ||  // 1101
      transition == 4  ||  // 0100
      transition == 2  ||  // 0010
      transition == 11) {  // 1011
    encoderLeft--;
  }

  // Clockwise detected
  if (transition == 14 ||  // 1110
      transition == 7  ||  // 0111
      transition == 1  ||  // 0001
      transition == 8) {   // 1000
    encoderLeft++;
  }

  lastEncodedLeft = current_state;
}

// ─── Right motor interrupt handler ────────────────────────────────
void updateRightEncoder() {
  int current_MSB = digitalRead(ENCODER_RIGHT_A);
  int current_LSB = digitalRead(ENCODER_RIGHT_B);

  int current_state = 0;
  if (current_MSB == 1) current_state = 2;
  if (current_LSB == 1) current_state += 1;

  int transition = lastEncodedRight * 4 + current_state;

  // Counter-clockwise detected
  if (transition == 13 ||  // 1101
      transition == 4  ||  // 0100
      transition == 2  ||  // 0010
      transition == 11) {  // 1011
    encoderRight--;
  }

  // Clockwise detected
  if (transition == 14 ||  // 1110
      transition == 7  ||  // 0111
      transition == 1  ||  // 0001
      transition == 8) {   // 1000
    encoderRight++;
  }

  lastEncodedRight = current_state;
}