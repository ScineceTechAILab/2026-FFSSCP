#!/usr/bin/env python3
"""
OPT101 光电传感器封装模块。

OPT101 本身输出模拟电压，不直接通过 I2C 或 GPIO 通信。
在本项目中，OPT101 的输出电压由 ADS1115 转换为数字量，
再由 Jetson Nano 通过 I2C 读取。

本模块只负责定义 OPT101 的传感器层接口，
实际电压读取由传入的 voltage_reader 完成。
"""


class OPT101Sensor:
    """
    OPT101 传感器抽象封装。

    voltage_reader 可以是真实硬件读取器 ADS1115Reader，
    也可以是无硬件环境下使用的 MockLightSensor。

    只要传入对象提供 read_voltage() 方法，
    OPT101Sensor 就可以统一读取电压。
    """

    def __init__(self, voltage_reader):
        """
        初始化 OPT101 传感器封装。

        参数:
            voltage_reader: 电压读取对象，必须提供 read_voltage() 方法。
        """
        self.voltage_reader = voltage_reader

    def read_voltage(self):
        """
        读取 OPT101 当前输出电压。

        返回:
            float，单位为 V。
        """
        return self.voltage_reader.read_voltage()

    def read_sample(self):
        """
        读取一条 OPT101 采样数据。

        当前仅返回电压值。后续如果进行标定，
        可以在这里扩展光照强度、标定系数等字段。
        """
        voltage = self.read_voltage()

        return {
            "voltage_v": voltage
        }
