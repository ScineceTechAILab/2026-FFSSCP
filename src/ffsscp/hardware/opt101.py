from typing import Any, Dict


class OPT101Sensor:
    def __init__(self, reader: Any) -> None:
        self.reader = reader

    def read_raw(self) -> int:
        if hasattr(self.reader, "read_raw"):
            return self.reader.read_raw()
        sample = self.reader.read_sample()
        return int(sample["raw_value"])

    def read_voltage(self) -> float:
        if hasattr(self.reader, "read_voltage"):
            return self.reader.read_voltage()
        sample = self.reader.read_sample()
        return float(sample["voltage_v"])

    def read_sample(self) -> Dict[str, float]:
        if hasattr(self.reader, "read_sample"):
            return self.reader.read_sample()
        raw_value = self.read_raw()
        voltage = self.read_voltage()
        return {"raw_value": raw_value, "voltage_v": voltage}
