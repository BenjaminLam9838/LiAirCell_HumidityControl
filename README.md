LiAirCell_Humidity Control
===
A humidity controlled gas flow for Li-Air Cell testing.  This is intended to be used for a Swagelok-type cell.

A pure O<sub>2</sub> stream is split between two mass-flow controllers (MFCs) with one of the streams humidified. These are recombined to produce a gas stream of desired humidity.  The output humidity is measured and the flow through each MFC is regulated by closed-loop feedback: 
<img width="968" alt="FlowDiagramSchematic" src="https://github.com/user-attachments/assets/1f5faf27-43f0-4f96-b58d-8f3220fa087e">

Software Configuration
===
First, download the application and install dependancies:
```bash
git clone https://github.com/BenjaminLam9838/LiAirCell_HumidityControl
cd LiAirCell_HumidityControl
pip install -r requirements.txt
```
The webapp is intended to be run on a local machine.  The python server runs on Flask and this handles all of the data processing and control systems.  It communicates with an Arduino over a Firmata protocol to poll the humidity sensors.  The web application makes requests to this Flask server to display the relevant information.
Connection to both MFCs and the sensors is required for the application to function properly.  These are outlined below.

### MFCs
Communication with the Alicat MFCs is done through [Alicat's python library](https://www.alicat.com/using-your-alicat/alicat-python-and-command-prompt-communication/). Click on the MFC in the Flow Diagram to bring up the connection settings:
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/39db4e3c-1609-4d49-ac07-07592e316a05">
- MFC Port: serial port the MFC is attached to

### Arduino + Firmata
Communication with the Arduino is done with Firmata.  The ```LAC_firmata.ino``` file must be uploaded to an Arduino and connected to the Flask server using the webapp.  Click on the sensor in the Flow Diagram to bring up the connection settings:
<img width="1510" alt="image" src="https://github.com/user-attachments/assets/852876c4-f6cb-4bea-a09a-94138dd9e8da">
- Arduino Port: serial port Arduino is attached to
- Sensor Address: I2C address of the sensor

_How the Firmata protocol works:_
The python server makes a sysex request with the same command ID as the I2C address of the sensor.  The Arduino then queries the sensor at that address for humidity/temperature data and echoes that back to the server as two floats.


Mechanical/Electrical
===
Main Parts List:
- Mass Flow Controller: Alicat MC-100SCCM-D-DB9M/5M
- Humidifier: Permapure MH-050-12P-2 12" Humidifier - Poly Fit/Shel
- Humidity/Temperature Sensor: [CC2D25S-SIP]([url](https://www.digikey.com/en/products/detail/amphenol-advanced-sensors/CC2D25S-SIP/4732678))

Connections between components is done with polypropylene tubing and push-to-connect fittings from McMaster (nominal size 1/8").  Stainless steel NPT fittings are used as needed, mainly for the mixing of the gas streams and for the humidity/temperature sensors.

### Humidity/Temperature Sensors
_In Progress_

