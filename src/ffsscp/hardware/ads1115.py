import time
from typing import Any, Dict, Optional


class ADS1115Reader:
    REG_CONVERSION = 0x00
    REG_CONFIG = 0x01

    CONFIG_OS_SINGLE = 0x8000
    CONFIG_MODE_SINGLE = 0x0100
    CONFIG_DR_128SPS = 0x0080
    CONFIG_COMP_DISABLE = 0x0003

    PGA_CONFIG = {
        6.144: (0x0000, 6.144),
        4.096: (0x0200, 4.096),
        2.048: (0x0400, 2.048),
        1.024: (0x0600, 1.024),
        0.512: (0x0800, 0.512),
        0.256: (0x0A00, 0.256),
    }

    MUX_SINGLE_ENDED = {
        0: 0x4000,
        1: 0x5000,
        2: 0x6000,
        3: 0x7000,
    }

    def __init__(
        self,
        bus_number: int = 1,
        address: int = 0x48,
        gain: float = 4.096,
        channel: int = 0,
        bus: Optional[Any] = None,
    ) -> None:
        if gain not in self.PGA_CONFIG:
            raise ValueError("Unsupported gain: {}".format(gain))
        if channel not in self.MUX_SINGLE_ENDED:
            raise ValueError("Unsupported channel: {}".format(channel))

        self.bus_number = bus_number
        self.address = address
        self.gain = gain
        self.channel = channel
        self.pga_bits, self.full_scale_voltage = self.PGA_CONFIG[gain]

        if bus is None:
            import smbus

            self.bus = smbus.SMBus(bus_number)
        else:
            self.bus = bus

    def __enter__(self) -> "ADS1115Reader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        if self.bus is not None and hasattr(self.bus, "close"):
            self.bus.close()
        self.bus = None

    def write_register(self, register: int, value: int) -> None:
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(self.address, register, [high_byte, low_byte])

    def read_register(self, register: int) -> int:
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        value = (data[0] << 8) | data[1]
        if value > 0x7FFF:
            value -= 0x10000
        return value

    def wait_conversion_ready(self, timeout: float = 0.1) -> None:
        start_time = time.time()
        while True:
            config_value = self.read_register(self.REG_CONFIG)
            if config_value & self.CONFIG_OS_SINGLE:
                return
            if time.time() - start_time > timeout:
                raise TimeoutError("ADS1115 conversion timeout")
            time.sleep(0.001)

    def read_raw(self, channel: Optional[int] = None) -> int:
        if channel is None:
            channel = self.channel
        if channel not in self.MUX_SINGLE_ENDED:
            raise ValueError("Unsupported channel: {}".format(channel))

        config = (
            self.CONFIG_OS_SINGLE
            | self.MUX_SINGLE_ENDED[channel]
            | self.pga_bits
            | self.CONFIG_MODE_SINGLE
            | self.CONFIG_DR_128SPS
            | self.CONFIG_COMP_DISABLE
        )
        self.write_register(self.REG_CONFIG, config)
        self.wait_conversion_ready()
        return self.read_register(self.REG_CONVERSION)

    def raw_to_voltage(self, raw_value: int) -> float:
        return raw_value * self.full_scale_voltage / 32768.0

    def read_voltage(self, channel: Optional[int] = None) -> float:
        raw_value = self.read_raw(channel)
        return self.raw_to_voltage(raw_value)

    def read_sample(self, channel: Optional[int] = None) -> Dict[str, Any]:
        if channel is None:
            channel = self.channel
        raw_value = self.read_raw(channel)
        voltage = self.raw_to_voltage(raw_value)
        return {
            "raw_value": raw_value,
            "voltage_v": voltage,
            "channel": "A{}".format(channel),
            "adc": "ADS1115",
        }
