#include <Firmata.h>
#include <Wire.h>

void setup() {
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION);
  Firmata.begin(57600);

  // Attach SysEx callback handler
  for (uint8_t i = 0; i < 0x50; i++)
    Firmata.attach(i, sysexCallback);

  Wire.begin();
}

void loop() {
  // Handle any incoming Firmata messages
  while (Firmata.available()) {
    Firmata.processInput();
  }
}

void sysexCallback(byte command, byte argc, byte* argv) {
  uint8_t* sensorData = readCC2(command);  // Read from ChipCap2 sensor
  byte dataBytes[5];
  dataBytes[0] = command;
  dataBytes[1] = sensorData[0];
  dataBytes[2] = sensorData[1];
  dataBytes[3] = sensorData[2];
  dataBytes[4] = sensorData[3];
  Firmata.sendSysex(command, sizeof(dataBytes), dataBytes);
  delete[] sensorData;  // Free dynamically allocated memory

  // Echo back the received SysEx message
  // switch (command) {
  //   case 0x10:
  //     {
  //       byte data[4];
  //       data[0] = 23;
  //       data[1] = 14;
  //       data[2] = 22;
  //       data[3] = 14;

  //       Firmata.sendSysex(command, 4, data);
  //       break;
  //     }

  //   case 0x13:
  //     {
  //       Firmata.sendSysex(command, argc, argv);
  //       break;
  //     }

  //   default:
  //     {
  //       uint8_t* sensorData = readCC2(command);  // Read from ChipCap2 sensor
  //       byte dataBytes[4];
  //       memcpy(dataBytes, sensorData, 4);
  //       Firmata.sendSysex(command, sizeof(dataBytes), dataBytes);
  //       delete[] sensorData;  // Free dynamically allocated memory
  //       break;
  //     }
  // }
}


uint8_t* readCC2(uint8_t cc_i2c_addr) {
  digitalWrite(LED_BUILTIN, HIGH);
  //Wake up the sensor from sleep mode
  Wire.beginTransmission(cc_i2c_addr);
  byte success = Wire.endTransmission(true);
  delay(50);

  //Read the data from the sensor:
  //  Data bytes AAHHHHHH HHHHHHHH TTTTTTTT TTTTTTXX
  //  A: status bits (00 for normal reading)
  //  H: Humidity Bits
  //  T: Temperature Bits
  //  X: Ignore
  uint8_t* rht = new uint8_t[4];

  Wire.beginTransmission(cc_i2c_addr);
  Wire.requestFrom(cc_i2c_addr, 4, true);
  rht[0] = Wire.read();
  rht[1] = Wire.read();
  rht[2] = Wire.read();
  rht[3] = Wire.read();
  Wire.endTransmission();

  digitalWrite(LED_BUILTIN, LOW);

  return rht;
}
