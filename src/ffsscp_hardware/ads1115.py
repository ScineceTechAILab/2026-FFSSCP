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


class ADS1115Reader:
    """
    ADS1115 单端输入读取器。

    该类负责：
    1. 配置 ADS1115 的输入通道、量程和采样模式；
    2. 读取 ADC 原始值；
    3. 将原始 ADC 数值换算为实际电压。
    """

    # ADS1115 寄存器地址
    REG_CONVERSION = 0x00
    REG_CONFIG = 0x01

    # ADS1115 配置位：单次转换、单次采样模式、128SPS、关闭比较器
    CONFIG_OS_SINGLE = 0x8000
    CONFIG_MODE_SINGLE = 0x0100
    CONFIG_DR_128SPS = 0x0080
    CONFIG_COMP_DISABLE = 0x0003

    # PGA 量程配置：
    # key 为满量程电压，value 为寄存器配置位和实际满量程值。
    PGA_CONFIG = {
        6.144: (0x0000, 6.144),
        4.096: (0x0200, 4.096),
        2.048: (0x0400, 2.048),
        1.024: (0x0600, 1.024),
        0.512: (0x0800, 0.512),
        0.256: (0x0A00, 0.256),
    }

    # 单端输入通道配置：A0~A3 分别相对 GND 测量。
    MUX_SINGLE_ENDED = {
        0: 0x4000,
        1: 0x5000,
        2: 0x6000,
        3: 0x7000,
    }

    def __init__(self, bus_number=1, address=0x48, gain=4.096):
        """
        初始化 ADS1115 读取器。

        参数:
            bus_number: I2C 总线编号，Jetson Nano 40Pin 常用 bus 1。
            address: ADS1115 I2C 地址，ADDR 接 GND 时为 0x48。
            gain: ADS1115 PGA 量程，默认 ±4.096V。
        """
        # 延迟导入 smbus，避免 mock 模式或无硬件环境下导入模块时报错。
        import smbus

        if gain not in self.PGA_CONFIG:
            raise ValueError("Unsupported gain: {}".format(gain))

        self.bus_number = bus_number
        self.address = address
        self.gain = gain
        self.pga_bits, self.full_scale_voltage = self.PGA_CONFIG[gain]

        # 打开指定 I2C 总线，例如 bus 1 对应 /dev/i2c-1。
        self.bus = smbus.SMBus(bus_number)

    def close(self):
        """
        关闭 I2C 总线。

        采集脚本退出时调用该方法，释放底层 I2C 资源。
        """
        self.bus.close()

    def write_register(self, register, value):
        """
        向 ADS1115 指定寄存器写入 16 位配置值。

        ADS1115 的寄存器宽度为 16 位，但 I2C 按字节发送，
        因此需要拆分为高 8 位和低 8 位。
        """
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        self.bus.write_i2c_block_data(
            self.address,
            register,
            [high_byte, low_byte]
        )

    def read_register(self, register):
        """
        从 ADS1115 指定寄存器读取 16 位数据。

        ADS1115 转换结果是有符号 16 位整数。当最高位为 1 时，
        需要按补码方式转换为 Python 中的负数。
        """
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        value = (data[0] << 8) | data[1]

        if value > 0x7FFF:
            value -= 0x10000

        return value

    def read_raw(self, channel=0):
        """
        读取指定单端通道的 ADC 原始值。

        参数:
            channel: ADS1115 通道编号，0~3 分别对应 A0~A3。

        返回:
            int，ADS1115 转换后的原始 ADC 数值。
        """
        if channel not in self.MUX_SINGLE_ENDED:
            raise ValueError("Unsupported channel: {}".format(channel))

        # 组合 ADS1115 配置寄存器：
        # 单次转换 + 指定通道 + 指定量程 + 单次模式 + 128SPS + 关闭比较器。
        config = (
            self.CONFIG_OS_SINGLE |
            self.MUX_SINGLE_ENDED[channel] |
            self.pga_bits |
            self.CONFIG_MODE_SINGLE |
            self.CONFIG_DR_128SPS |
            self.CONFIG_COMP_DISABLE
        )

        self.write_register(self.REG_CONFIG, config)

        # 等待 ADS1115 完成一次转换。128SPS 下单次转换约 7.8ms。
        time.sleep(0.01)

        return self.read_register(self.REG_CONVERSION)

    def raw_to_voltage(self, raw_value):
        """
        将 ADS1115 原始 ADC 数值换算为电压。

        ADS1115 为 16 位 ADC，正向满量程约对应 32768。
        当前默认量程为 ±4.096V，因此 1 bit 约等于 0.125mV。
        """
        return raw_value * self.full_scale_voltage / 32768.0

    def read_voltage(self, channel=0):
        """
        读取指定通道电压值。

        参数:
            channel: ADS1115 通道编号，0~3 分别对应 A0~A3。

        返回:
            float，单位为 V。
        """
        raw_value = self.read_raw(channel)
        voltage = self.raw_to_voltage(raw_value)

        return voltage

    def read_sample(self, channel=0):
        """
        读取一条完整采样数据。

        返回字典包含 ADC 名称、通道、原始值和电压值，
        便于上层脚本直接写入 CSV。
        """
        raw_value = self.read_raw(channel)
        voltage = self.raw_to_voltage(raw_value)

        return {
            "raw_value": raw_value,
            "voltage_v": voltage,
            "channel": "A{}".format(channel),
            "adc": "ADS1115"
        }
