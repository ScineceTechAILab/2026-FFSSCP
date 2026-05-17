#!/usr/bin/env python3
"""
ADS1115 模数转换器读取模块。

本模块通过 Jetson Nano 的 I2C 总线读取 ADS1115 ADC 数据，
用于将 OPT101 输出的模拟电压转换为数字电压值。

默认硬件配置：
- I2C 总线：bus 1，对应 Jetson Nano 常用的 /dev/i2c-1
- I2C 地址：0x48，对应 ADS1115 ADDR 接 GND
- 默认量程：±4.096V
"""

import time
from typing import Any, Dict, Optional


class ADS1115Reader:
    """
    ADS1115 单端输入读取器。

    该类负责：
    1. 配置 ADS1115 的输入通道、量程和采样模式；
    2. 读取 ADC 原始值；
    3. 将原始 ADC 数值换算为实际电压。
    """

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
        """
        初始化 ADS1115 读取器。

        参数:
            bus_number: I2C 总线编号，Jetson Nano 40Pin 常用 bus 1。
            address: ADS1115 I2C 地址，ADDR 接 GND 时为 0x48。
            gain: ADS1115 PGA 量程，默认 ±4.096V。
            channel: 默认读取通道，0~3 分别对应 A0~A3。
            bus: 可注入的 I2C bus，对测试或 mock 场景更方便。
        """
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
        """
        关闭 I2C 总线。
        """
        if self.bus is not None and hasattr(self.bus, "close"):
            self.bus.close()
        self.bus = None

    def write_register(self, register: int, value: int) -> None:
        """
        向 ADS1115 指定寄存器写入 16 位配置值。
        """
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(self.address, register, [high_byte, low_byte])

    def read_register(self, register: int) -> int:
        """
        从 ADS1115 指定寄存器读取 16 位数据。
        """
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        value = (data[0] << 8) | data[1]

        if value > 0x7FFF:
            value -= 0x10000

        return value

    def wait_conversion_ready(self, timeout: float = 0.1) -> None:
        """
        等待 ADS1115 单次转换完成。
        """
        start_time = time.time()

        while True:
            config_value = self.read_register(self.REG_CONFIG)

            if config_value & self.CONFIG_OS_SINGLE:
                return

            if time.time() - start_time > timeout:
                raise TimeoutError("ADS1115 conversion timeout")

            time.sleep(0.001)

    def read_raw(self, channel: Optional[int] = None) -> int:
        """
        读取指定单端通道的 ADC 原始值。
        """
        if channel is None:
            channel = self.channel

        if channel not in self.MUX_SINGLE_ENDED:
            raise ValueError("Unsupported channel: {}".format(channel))

        config = (
            self.CONFIG_OS_SINGLE |
            self.MUX_SINGLE_ENDED[channel] |
            self.pga_bits |
            self.CONFIG_MODE_SINGLE |
            self.CONFIG_DR_128SPS |
            self.CONFIG_COMP_DISABLE
        )

        self.write_register(self.REG_CONFIG, config)
        self.wait_conversion_ready()

        return self.read_register(self.REG_CONVERSION)

    def raw_to_voltage(self, raw_value: int) -> float:
        """
        将 ADS1115 原始 ADC 数值换算为电压。
        """
        return raw_value * self.full_scale_voltage / 32768.0

    def read_voltage(self, channel: Optional[int] = None) -> float:
        """
        读取指定通道电压值。
        """
        raw_value = self.read_raw(channel)
        return self.raw_to_voltage(raw_value)

    def read_sample(self, channel: Optional[int] = None) -> Dict[str, Any]:
        """
        读取一条完整采样数据。
        """
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
