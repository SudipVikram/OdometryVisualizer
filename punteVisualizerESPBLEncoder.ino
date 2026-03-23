/* 
* Code for Punte Robot's visualizer on the ESP32 side
* code by Beyond Apogee, Nepal
* Author: Sudip Vikram Adhikari
*/

#include <BluetoothSerial.h>
BluetoothSerial SerialBT;

#include <Wire.h>
#include <VL53L0X.h>

// using FreeRTOS for handling TOF
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// global variables
volatile int tof_distance_mm = -1;
TaskHandle_t tofTaskHandle = NULL;

VL53L0X sensor; // Time of Flight Sensor
#define SDA_PIN 4
#define SCL_PIN 15

#define ENCODER_LEFT_A   13   // C1 Phase A left motor
#define ENCODER_LEFT_B   12   // C2 Phase B left motor
#define ENCODER_RIGHT_A  32   // C1 Phase A right motor
#define ENCODER_RIGHT_B  33   // C2 Phase B right motor

// Motor PWM pins
#define MOTOR_LEFT_IA    25
#define MOTOR_LEFT_IB    26
#define MOTOR_RIGHT_IA   27
#define MOTOR_RIGHT_IB   14

// speed of Punte
const int MOTOR_SPEED = 80;

// ─── Left motor variables ────────────────────────────────────────
volatile int lastEncodedLeft = 0;
volatile long encoderLeft    = 0;

// ─── Right motor variables ───────────────────────────────────────
volatile int lastEncodedRight = 0;
volatile long encoderRight    = 0;

void setup() {
  Serial.begin(115200);
  delay(100);

  Wire.begin(SDA_PIN, SCL_PIN);

  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("VL53L0X not detected! Check wiring.");
    while (1) delay(10);
  }

  Serial.println("VL53L0X found. Measuring distance...");
  xTaskCreate(
    tofTask,          // function name
    "TOF Reader",     // task name(for debugging)
    4096,             // stack size - 4KB
    NULL,             // no parameters
    1,                // priority (1=low, same as loop)
    &tofTaskHandle    // handle (optional)
  );

  
  // Optional: make it more accurate (slower)
  sensor.setMeasurementTimingBudget(200000);  // 200 ms

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
  Serial.print(", R:");
  Serial.print(encoderRight);
  Serial.print(", TOF: ");
  Serial.println(tof_distance_mm);

  //delay(40);   // ≈25 Hz – reasonable compromise between responsiveness and serial load

  //int distance = sensor.readRangeSingleMillimeters();

  /*if (sensor.timeoutOccurred()) {
    Serial.println("Timeout!");
  } else {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" mm");
  }*/

  // ─── Send encoders every ~50 ms ────────────────────────
    static unsigned long t0 = 0;
    if (millis() - t0 >= 50) {
        t0 = millis();
        SerialBT.print("L:");
        SerialBT.print(encoderLeft);
        SerialBT.print(", R:");
        SerialBT.print(encoderRight);
        SerialBT.print(", TOF:");
        SerialBT.println(tof_distance_mm);
    }

    // ─── Receive motor commands ────────────────────────────
    if (SerialBT.available()) {
        String cmd = SerialBT.readStringUntil('\n');
        cmd.trim();

        if (cmd == "FORWARD"){ /* both motors forward */ 
          analogWrite(MOTOR_LEFT_IA, MOTOR_SPEED);
          analogWrite(MOTOR_LEFT_IB, 0);
          analogWrite(MOTOR_RIGHT_IA, MOTOR_SPEED);
          analogWrite(MOTOR_RIGHT_IB, 0);
        } else if (cmd == "BACKWARD"){ /* both backward */ 
          analogWrite(MOTOR_LEFT_IA, 0);
          analogWrite(MOTOR_LEFT_IB, MOTOR_SPEED);
          analogWrite(MOTOR_RIGHT_IA, 0);
          analogWrite(MOTOR_RIGHT_IB, MOTOR_SPEED);
        } else if (cmd == "LEFT"){ /* move left */ 
          analogWrite(MOTOR_LEFT_IA, 0);
          analogWrite(MOTOR_LEFT_IB, MOTOR_SPEED);
          analogWrite(MOTOR_RIGHT_IA, MOTOR_SPEED);
          analogWrite(MOTOR_RIGHT_IB, 0);
        } else if (cmd == "RIGHT"){ /* move right */
          analogWrite(MOTOR_LEFT_IA, MOTOR_SPEED);
          analogWrite(MOTOR_LEFT_IB, 0);
          analogWrite(MOTOR_RIGHT_IA, 0);
          analogWrite(MOTOR_RIGHT_IB, MOTOR_SPEED); 
        } else if (cmd == "STOP"){ /* STOP */
          analogWrite(MOTOR_LEFT_IA, 0);
          analogWrite(MOTOR_LEFT_IB, 0);
          analogWrite(MOTOR_RIGHT_IA, 0);
          analogWrite(MOTOR_RIGHT_IB, 0);
        }
    }
}

// TOF reading task function
void tofTask(void *pvParameters){
  for(;;){
    int mm = sensor.readRangeSingleMillimeters();

    if(!sensor.timeoutOccurred()){
      tof_distance_mm = mm;
    } else {
      tof_distance_mm = -2;
    }

    vTaskDelay(pdMS_TO_TICKS(120)); // read ~8 times per second
    //or vTaskDelay(pdMS_TO_TICKS(200)); // for slower, more accurate readings
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