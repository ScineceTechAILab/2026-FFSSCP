import math
import random
import time


class MockLightSensor:
    def __init__(self, base_raw: int = 9600, amplitude_raw: int = 2800, noise_raw: int = 180):
        self.base_raw = base_raw
        self.amplitude_raw = amplitude_raw
        self.noise_raw = noise_raw
        self.start_time = time.time()

    def read_raw(self) -> int:
        elapsed = time.time() - self.start_time
        signal = self.amplitude_raw * math.sin(elapsed)
        noise = random.uniform(-self.noise_raw, self.noise_raw)
        raw_value = int(self.base_raw + signal + noise)
        return max(raw_value, 0)

    def raw_to_voltage(self, raw_value: int) -> float:
        return raw_value * 4.096 / 32768.0

    def read_voltage(self) -> float:
        return self.raw_to_voltage(self.read_raw())

    def read_sample(self):
        raw_value = self.read_raw()
        return {
            "raw_value": raw_value,
            "voltage_v": self.raw_to_voltage(raw_value),
            "channel": "A0",
            "adc": "mock",
        }
