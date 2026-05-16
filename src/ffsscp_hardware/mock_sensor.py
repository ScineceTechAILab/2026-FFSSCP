#!/usr/bin/env python3

import math
import random
import time


class MockLightSensor:
    def __init__(self, base_voltage=1.2, amplitude=0.4, noise=0.03):
        self.base_voltage = base_voltage
        self.amplitude = amplitude
        self.noise = noise
        self.start_time = time.time()

    def read_voltage(self):
        elapsed = time.time() - self.start_time
        signal = self.amplitude * math.sin(elapsed)
        random_noise = random.uniform(-self.noise, self.noise)
        voltage = self.base_voltage + signal + random_noise

        if voltage < 0:
            voltage = 0.0

        return voltage
