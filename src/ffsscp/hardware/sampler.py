import time
from datetime import datetime
from typing import Dict, List

from ffsscp.hardware.ads1115 import ADS1115Reader
from ffsscp.hardware.mock_sensor import MockLightSensor
from ffsscp.hardware.opt101 import OPT101Sensor


def create_sensor(mode: str, bus: int = 1, address: str = "0x48", channel: int = 0, gain: float = 4.096) -> OPT101Sensor:
    if mode == "mock":
        return OPT101Sensor(MockLightSensor())
    if mode == "hardware":
        reader = ADS1115Reader(
            bus_number=bus,
            address=int(address, 16),
            gain=gain,
            channel=channel,
        )
        return OPT101Sensor(reader)
    raise ValueError("Unsupported mode: {}".format(mode))


def collect_samples(sensor: OPT101Sensor, count: int, interval: float, mode: str) -> List[Dict[str, object]]:
    rows = []
    for index in range(1, count + 1):
        sample = sensor.read_sample()
        rows.append(
            {
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                "sensor": "OPT101",
                "adc": sample.get("adc", mode),
                "channel": sample.get("channel", "A0"),
                "mode": mode,
                "sample_index": index,
                "raw_value": sample["raw_value"],
                "voltage_v": sample["voltage_v"],
            }
        )
        if index < count:
            time.sleep(interval)
    return rows
