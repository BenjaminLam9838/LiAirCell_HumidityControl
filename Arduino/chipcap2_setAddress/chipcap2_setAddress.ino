/**
 * chipcap2_setAddress.ino
 * Resets the I2C address of the device.  Default address is 0x28 (010 1000)
 * Available addresses are 0x00 to 0x7F (111 1111) -> full range of 7 bit I2C address

 * After writing the new address to the device, changing to normal mode or power cycling updates the address.  
 * While still in command mode, the device keeps the old address, so the normal mode request should be made 
 * with the old address
*/

#include "Wire.h"

#define POWER_PIN1 3
#define POWER_PIN2 4
#define POWER_PIN3 5
#define CC_OLD_ADDR 0x28
#define CC_NEW_ADDR 0x32

void setup() {
  Wire.begin();
  Wire.setWireTimeout(10000 /* us */, true /* reset_on_timeout */);

  Serial.begin(9600);
  pinMode(POWER_PIN1, OUTPUT);  //Configure the power pin
  pinMode(POWER_PIN2, OUTPUT);
  pinMode(POWER_PIN3, OUTPUT);
  pinMode(A0, INPUT);


  bool cmdStarted = startCommandMode(CC_OLD_ADDR);    //Don't put anything above this (no power on), it messes things up for some reason
  if (cmdStarted) {
    Serial.println("COMMAND STARTED");

    readCommandMode(CC_OLD_ADDR, 0x1C);  //Read the 0x1C address (CUST CONFIG, default is 0x0028)
    Serial.println("REGISTER READ");
    writeCommandMode(CC_OLD_ADDR, 0x5C, CC_NEW_ADDR & 0x00FF);
    Serial.println("REGISTER WRITTEN");
    readCommandMode(CC_OLD_ADDR, 0x1C);  //Read the 0x1C address to confirm write
    Serial.println("REGISTER READ");

    startNormalMode(CC_OLD_ADDR);  //Normal mode locks in the new address by ending command mode
    scanI2CBus();
    readCC2(CC_NEW_ADDR);
  }

  Serial.println("NOT WRITTEN");
}


void loop() {
  scanI2CBus();
  readCC2(CC_NEW_ADDR);
  readCC2(CC_OLD_ADDR);
  delay(1000);
}

void powerLOW() {
  digitalWrite(POWER_PIN1, LOW);
  digitalWrite(POWER_PIN2, LOW);
  digitalWrite(POWER_PIN3, LOW);
}

void powerHIGH() {
  digitalWrite(POWER_PIN1, HIGH);
  digitalWrite(POWER_PIN2, HIGH);
  digitalWrite(POWER_PIN3, HIGH);
}


// Enters command mode (Only valid during first 10ms after power-on) with command byte 0xA0
bool startCommandMode(uint8_t I2C_addr) {
  Serial.println(I2C_addr, HEX);
  scanI2CBus();
  powerLOW();
  delay(500);
  powerHIGH();
  // delay(5);
  // Serial.println("Power");

  Wire.beginTransmission(I2C_addr);
  Wire.write(0xA0);
  Wire.write(0);
  Wire.write(0);
  uint8_t error = Wire.endTransmission(true);

  Serial.println("Transmitted");
  if (error == 0) {
    Serial.println("Command mode started successfully.");
    delay(5);
    return true;
  } else {
    Serial.print("Failed to start command mode, error: ");
    Serial.println(error);
    return false;
  }
}

// Enters normal mode with command byte 0x80
void startNormalMode(uint8_t I2C_addr) {
  Wire.beginTransmission(I2C_addr);
  Wire.write(0x80);
  Wire.write(0);
  Wire.write(0);
  uint8_t error = Wire.endTransmission();

  if (error == 0) {
    Serial.println("Normal mode started successfully.");
  } else {
    Serial.print("Failed to start normal mode, error: ");
    Serial.println(error);
  }
  delay(5);
}

void writeCommandMode(uint8_t I2C_addr, uint8_t commandByte, uint16_t writeData) {
  // Read 0x16 to 0x1F addresses
  if (commandByte < 0x56 || commandByte > 0x5F)
    return;

  Serial.print("Writing 0x");
  for (int i = 3; i >= 0; i--) {
    Serial.print((writeData >> i * 4) & B1111, HEX);
  }
  Serial.print(" to 0x");
  Serial.println(commandByte & 0x1F, HEX);  //Memory address is this command byte with the 0W00 0000 flipped

  // Set the memory address to write to
  Wire.beginTransmission(I2C_addr);
  Wire.write(commandByte);     // Command byte: EEPROM address to write to
  Wire.write(writeData >> 8);  // Send the bytes to write
  Wire.write(writeData & 0xFF);
  Wire.endTransmission();
  delay(15);  //Response takes 12ms

  // Read the response, should be what I just wrote to the register
  commandResponse(I2C_addr, commandByte);
}

void readCommandMode(uint8_t I2C_addr, uint8_t commandByte) {
  // Read 0x16 to 0x1F addresses
  if (commandByte < 0x16 || commandByte > 0x1F)
    return;

  // Set the memory address to read from
  Wire.beginTransmission(I2C_addr);
  Wire.write(commandByte);  // Command byte: EEPROM address to read from
  Wire.write(0);            //Reading, so no data to transmit
  Wire.write(0);
  Wire.endTransmission();
  delay(1);  //Response takes 100µs

  // Read the response: what is contained at the queried address
  commandResponse(I2C_addr, commandByte);
}

void commandResponse(uint8_t I2C_addr, uint8_t commandByte) {
  uint8_t edat[3];  //Array to save the response
  Wire.beginTransmission(I2C_addr);
  Wire.requestFrom(I2C_addr, 3, true);
  edat[0] = Wire.read();
  edat[1] = Wire.read();
  edat[2] = Wire.read();
  Wire.endTransmission();

  //Print out the register data in Binary
  Serial.print("Response of ");
  Serial.print(commandByte, HEX);
  Serial.print(" command: ");  //Command Byte response
  Serial.print(edat[0], BIN);
  Serial.print(" | ");  //Status byte
  Serial.print(edat[1], BIN);
  Serial.print(" | ");         //Data MSB
  Serial.print(edat[2], BIN);  //Data LSB

  //Print out the register data in hex (2 bytes: 0xHHHH)
  Serial.print("\n\tData HEX: 0x");
  uint16_t readData = edat[1] << 8 | edat[2];
  for (int i = 3; i >= 0; i--) {
    Serial.print((readData >> i * 4) & 0xF, HEX);  //Get 4 bits at a time, starting with MSB and print as HEX
  }
  Serial.println();
}


void scanI2CBus() {
  // put your main code here, to run repeatedly:
  int nDevices = 0;

  Serial.println("Scanning...");

  for (byte address = 1; address < 127; ++address) {
    // The i2c_scanner uses the return value of
    // the Wire.endTransmission to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission(true);

    if (error == 0) {
      Serial.print("I2C device found at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.print(address, HEX);
      Serial.println("  !");

      ++nDevices;
    } else if (error == 4) {
      Serial.print("Unknown error at address 0x");
      if (address < 16) {
        Serial.print("0");
      }
      Serial.println(address, HEX);
    }
  }
  if (nDevices == 0) {
    Serial.println("No I2C devices found\n");
  } else {
    Serial.println("done\n");
  }

  delay(1000);
}

uint8_t* readCC2(uint8_t cc_i2c_addr) {
  //Wake up the sensor from sleep mode
  Wire.beginTransmission(cc_i2c_addr);
  byte success = Wire.endTransmission(true);
  Serial.print("Polling 0x");
  Serial.println(cc_i2c_addr, HEX);
  Serial.print("Data Fetch (0 is normal): ");
  Serial.println(success);
  delay(50);

  //Read the data from the sensor:
  //  Data bytes AAHHHHHH HHHHHHHH TTTTTTTT TTTTTTXX
  //  A: status bits (00 for normal reading)
  //  H: Humidity Bits
  //  T: Temperature Bits
  //  X: Ignore
  uint8_t rht[4];

  Wire.beginTransmission(cc_i2c_addr);
  Wire.requestFrom(cc_i2c_addr, 4, true);
  rht[0] = Wire.read();
  rht[1] = Wire.read();
  rht[2] = Wire.read();
  rht[3] = Wire.read();
  Wire.endTransmission();
  uint8_t status = rht[0] >> 6;

  //Print status
  Serial.print("\t Status = ");
  Serial.print(status, BIN);

  //Print data bytes (4)
  Serial.print("\n\t");
  for (int i = 0; i < 4; i++) {
    for (int ii = 7; ii >= 0; ii--)
      Serial.print((rht[i] >> ii) & 1, BIN);
    Serial.print(" | ");
  }

  //Convert humidity and temperature values into floats and print
  float* data = new float[2];
  data[0] = float((rht[0] & B00111111) << 8 | rht[1]) / 0x4000 * 100.0;  //Humidity
  data[1] = float((rht[2] << 6) + (rht[3] >> 2)) / 0x4000 * 165 - 40;    //Temperature
  Serial.print("H = ");
  Serial.print(data[0]);
  Serial.print(" T = ");
  Serial.println(data[1]);

  return rht;
}
