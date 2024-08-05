LiAirCell_Humidity Control
===

A pure O<sub>2</sub> stream is split between two mass-flow controllers (MFCs) with one of the streams humidified. These are recombined to produce a gas stream of desired humidity.  The output humidity is measured and the flow through each MFC is regulated by closed-loop feedback: 
<img width="993" alt="Screen Shot 2024-08-05 at 1 11 18 PM" src="https://github.com/user-attachments/assets/a1dbc263-17f0-4de9-a945-78252817a799">



Software Configuration
===
First, download the application and install dependencies:
```bash
git clone https://github.com/BenjaminLam9838/LiAirCell_HumidityControl
cd LiAirCell_HumidityControl
```

Create a virtual environment and install the dependencies.  This app was built on Python 3.9.13 ([pyFirmata has issues in 3.11 [1]](#1-pyfirmata-has-issues-in-311))
```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The webapp is intended to be run on a local machine.  The python server runs on Flask and this handles all of the data processing and control systems.  It communicates with an Arduino over a Firmata protocol to poll the humidity sensors.  The web application makes requests to this Flask server to display the relevant information.
Connection to both MFCs and the sensors is required for the application to function properly.  These are outlined below.

### MFCs
Communication with the Alicat MFCs is done through [Alicat's python library](https://www.alicat.com/using-your-alicat/alicat-python-and-command-prompt-communication/). Click on the MFC in the Flow Diagram to bring up the connection settings:
![image](https://github.com/user-attachments/assets/358e5860-da27-4229-aff6-899b0483c947)

- MFC Port: serial port the MFC is attached to

### Arduino + Firmata
> [!IMPORTANT]
> Application requires connection to Arduino to function. Arduino serves as sensor controller, so without a connection, we have no sensors.

Communication with the Arduino is done with Firmata.  The ```LAC_firmata.ino``` file must be uploaded to an Arduino and connected to the Flask server using the webapp.  Click on the sensor in the Flow Diagram to bring up the connection settings:
![image](https://github.com/user-attachments/assets/c39bb345-d019-4eba-9cba-07edf16e6e1d)

- Sensor Address: I2C address of the sensor

_How the Firmata protocol works:_
The python server makes a sysex request with the same command ID as the I2C address of the sensor.  The Arduino then queries the sensor at that address for humidity/temperature data and echoes that back to the server as two floats.


Mechanical/Electrical
===
Main Parts List:
- Mass Flow Controller: [Alicat MC-100SCCM-D-DB9M/5M](https://www.alicat.com/gas-products/laminar-dp-mass-flow-meters-and-controllers/)
- Humidifier: [Permapure MH-050-12P-2 12" Humidifier - Poly Fit/Shel](https://www.permapure.com/environmental-scientific/products/gas-humidification/mh-series-humidifiers/)
- Humidity/Temperature Sensor: [CC2D25S-SIP](https://www.digikey.com/en/products/detail/amphenol-advanced-sensors/CC2D25S-SIP/4732678)

Connections between components is done with polypropylene tubing and push-to-connect fittings from McMaster (nominal size 1/8").  Stainless steel NPT fittings are used as needed, mainly for the mixing of the gas streams and for the humidity/temperature sensors.

### Humidity/Temperature Sensors
The CC2D25S-SIP sensor is used for this project. This is a small sensor that communicates over I2C.  The default address is ```0x28```. The ```chipcap2_setAddress.ino``` script is used to reset the I2C address of the component.
These sensors are contained in a [1/8" NPT pipe nipple](https://www.mcmaster.com/4830K111/) and filled with epoxy.  This can be screwed into a T-fitting for inline gas measurement:

<p align="center">
<img src='https://github.com/user-attachments/assets/4dea40d3-c7f1-4583-9557-30a6555dddc7' width=700 align=center>
</p>


Notes
===
#### [1] pyFirmata has issues in 3.11
[pyFirmata's Github](https://github.com/tino/pyFirmata/tree/master) says it runs on python 3.7.

When calling ```board = pyfirmata.Arduino('/dev/tty.usbmodem21101')```, an AttributeError is thrown: ```AttributeError: module 'inspect' has no attribute 'getargspec'. Did you mean: 'getargs'?```.
ChatGPT says:
> The error you're encountering is due to the use of the inspect.getargspec method in pyfirmata, which has been deprecated and removed in Python 3.11. Instead, inspect.getfullargspec should be used.

#### To do
- [x] Connection/display with humidity sensors
- [x] Connection/display with MFCs
- [ ] Control System
- [ ] Assemble full gas-flow integration

