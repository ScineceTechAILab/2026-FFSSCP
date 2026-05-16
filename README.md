# 2026-FFSSCP_Hardware_Driver

FFSSCP means Fracturing Flowback Fluid Suspended Solids Concentration Prediction.

This repository contains the hardware driver and optical data acquisition system for fracturing flowback fluid suspended solids concentration prediction using Jetson Nano, OPT101, and ADS1115.

## Hardware

- Jetson Nano 2GB
- OPT101 light sensor
- ADS1115 ADC module
- Light source
- Fracturing flowback fluid sample container

## Functions

- ADS1115 I2C communication
- OPT101 optical voltage acquisition
- ADC raw value to voltage conversion
- CSV data logging
- Interface reserved for concentration prediction

