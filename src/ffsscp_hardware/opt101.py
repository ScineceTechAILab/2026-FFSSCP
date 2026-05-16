#!/usr/bin/env python3


class OPT101Sensor:
    def __init__(self, voltage_reader):
        self.voltage_reader = voltage_reader

    def read_voltage(self):
        return self.voltage_reader.read_voltage()

    def read_sample(self):
        voltage = self.read_voltage()

        return {
            "voltage_v": voltage
        }
