LiAirCell_Humidity Control
===
Software for a humidity controlled gas flow for Li-Air Cell testing.  This is intended to be used for a Swagelok-type cell.

A pure O<sub>2</sub> stream is split between two mass-flow controllers (MFCs) and one of the streams is humidified. These are recombined to produce a gas stream of desired humidity.  The output humidity is measured and the flow through each MFC is regulated by closed-loop feedback: 
<img width="968" alt="FlowDiagramSchematic" src="https://github.com/user-attachments/assets/1f5faf27-43f0-4f96-b58d-8f3220fa087e">

Installation
===
```bash
git clone 
```


Mechanical/Electrical
===
Parts List:
- Mass Flow Controller: Alicat MC-100SCCM-D-DB9M/5M
- Humidifier: Permapure MH-050-12P-2 12" Humidifier - Poly Fit/Shel
- Humidity/Temperature Sensor: [CC2D25S-SIP]([url](https://www.digikey.com/en/products/detail/amphenol-advanced-sensors/CC2D25S-SIP/4732678))

