/*
geigerInterface.ino

Code to read counts per second and minute from a geiger counter connected to a Texas instruments SN74LV8154 counter IC by ThreeSixes (https://github.com/ThreeSixes)

Wiring setup:

Geiger counter optoisoloator output connected to pin 1 of the SN74LV8154.

The collector of the optoisolator is connected to +5v.
The emitter of the optoisoloator is pulled low by a 3.3K resistor and is tied to pin 1 of the SN74LV8154.

Arduino -> SN74LV8154 pin connections:
+5v -> 20 VCC
+5v -> 5 _GBL_
+5v -> 6 _GBU_
GND -> 10 GND
D2  -> 3 _GAL_
D3  -> 4 _GAU_
D4  -> 7 RCLK
D5  -> 11 _CCLR_
D6  -> 19 Data bus (LSB)
D7  -> 18 Data bus 
D8  -> 17 Data bus 
D9  -> 16 Data bus 
D10 -> 15 Data bus 
D11 -> 14 Data bus 
D12 -> 13 Data bus 
D13 -> 12 Data bus (MSB)
*/

// Uncomment to debug.
#define debugOn

// "Serial port" speed.
#define serialSpeed 115200

// Comment this out to disable i2c interface in slave mode.
#define isI2CSlave

// If we are going to be an I2C slave include the things we need to do so.
#ifdef isI2CSlave
  // Include I2C libraries.
  #include <Wire.h>

  // Set up I2C address.
  #define i2cAddr 0x35
#endif

// Control pins.
int galPin  = 2;
int gauPin  = 3;
int rclkPin = 4;
int cclrPin = 5;

// Digital bus pin arragment.
int digitalBusPin = 6; // Bus starts at D6
int digitalBusLen = 8; // 8-bit bus.

// Store counts per second.
unsigned int currentCount = 0;

// Clear the counter IC's buffer.
void counterClear() {
  // Send the clear pulse.
  digitalWrite(cclrPin, LOW);
  delay(1); // Wait 1 ms.
  digitalWrite(cclrPin, HIGH);
  
  return;
}

// Load the counts into the buffer for retrieval.
void counterLoadSample() {
  // Send the RCLK pulse.
  digitalWrite(rclkPin, LOW);
  delay(1); // Wait 1 ms.
  digitalWrite(rclkPin, HIGH);
  
  return;
}

// Read the 8-bit bus.
uint8_t readDigitalBus() {
  // 8-bit unsinged int.
  uint8_t retVal = 0;
  
  // Set each digital bus line to input.
  for(int i = 0; i < digitalBusLen; i++) {
    // Read a bit, and shift it into place.
    retVal = retVal | (digitalRead(digitalBusPin + i) << i);
  }
  
  return retVal;
}

// Get the counter data.
unsigned int counterGetSample() {
  // Set up a 16-bit return value.
  unsigned int retVal = 0;
  unsigned int msb = 0;
  unsigned int lsb = 0;
  
  // Get the 8 bits containing LSB.
  digitalWrite(galPin, LOW);
  digitalWrite(gauPin, HIGH);
  //delay(1);
  
  // Get the bits from the digital bus.
  lsb = readDigitalBus();
  
  // Get the 8 bits containing MSB.
  digitalWrite(galPin, HIGH);
  digitalWrite(gauPin, LOW);
  //delay(1);
  
  // Get the bits from the digital bus.
  msb = readDigitalBus();
  
  // Set IDGAF mode again.
  digitalWrite(galPin, HIGH);
  digitalWrite(gauPin, HIGH);
  
  // Concat MSB and LSB.
  retVal = (msb << 8) | lsb;
  
  #ifdef debugOn
  Serial.print("LSB:   0x");
  Serial.println(lsb, HEX); 
  Serial.print("MSB:   0x");
  Serial.println(msb, HEX);
  Serial.print("16BIT: 0x");
  Serial.println(retVal, HEX);
  #endif
  
  return retVal;
}

#ifdef isI2CSlave
// Send counts back.
void i2cTxData() {
  // Send MSB
  Wire.write(currentCount >> 8);
  // Send LSB
  Wire.write(currentCount & 0xff);

  return;
}
#endif

// Set up the Arduino's pins and serial.
void setup() {
  // Serial out.
  Serial.begin(serialSpeed);
  
  #ifdef isI2CSlave
  // Bring up I2C bus.
  Wire.begin(i2cAddr);
  // Set up request handler.
  Wire.onRequest(i2cTxData);
  #endif
  
  // GAL pin
  pinMode(galPin, OUTPUT);
  digitalWrite(galPin, HIGH);
  
  // GAU pin
  pinMode(gauPin, OUTPUT);
  digitalWrite(gauPin, HIGH);
  
  // RCLK pin
  pinMode(rclkPin, OUTPUT);
  digitalWrite(rclkPin, HIGH);
  
  // CCLR pin
  pinMode(cclrPin, OUTPUT);
  digitalWrite(cclrPin, HIGH);
  
  // Set each digital bus line to input.
  for(int i = 0; i < digitalBusLen; i++) {
    // Set target to input.
    digitalWrite(digitalBusPin + i, INPUT);
  }
}

void loop() {
  // Clear the counter.
  counterClear();
  
  // Wait 1 second.
  delay(1000);
  
  // Load counter data into registers.
  counterLoadSample();
  
  // Read the registers, update global counts.
  currentCount = counterGetSample();
    
  Serial.print("CPS: ");
  Serial.println(currentCount);
  Serial.println("--");
}
