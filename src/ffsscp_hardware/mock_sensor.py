#!/usr/bin/env python3
"""
模拟光照传感器模块。

在没有 ADS1115 或 OPT101 实物时，本模块用于生成模拟电压数据，
方便测试 CSV 记录、命令行参数和整体采集流程。

模拟电压由三部分组成：
1. 基础电压；
2. 随时间变化的正弦波；
3. 少量随机噪声。
"""

import math
import random
import time


class MockLightSensor:
    """
    模拟光照传感器。

    该类提供与真实电压读取器相同的 read_voltage() 接口，
    因此可以在无硬件环境下替代 ADS1115Reader 使用。
    """

    def __init__(self, base_voltage=1.2, amplitude=0.4, noise=0.03):
        """
        初始化模拟传感器参数。

        参数:
            base_voltage: 基础电压值，单位为 V。
            amplitude: 正弦波动幅度，单位为 V。
            noise: 随机噪声最大幅度，单位为 V。
        """
        self.base_voltage = base_voltage
        self.amplitude = amplitude
        self.noise = noise
        self.start_time = time.time()

    def read_voltage(self):
        """
        生成一条模拟电压数据。

        返回:
            float，模拟电压值，单位为 V。
        """
        # 根据程序运行时间生成一个缓慢变化的正弦信号。
        elapsed = time.time() - self.start_time
        signal = self.amplitude * math.sin(elapsed)

        # 添加少量随机噪声，使模拟数据更接近真实传感器波动。
        random_noise = random.uniform(-self.noise, self.noise)

        voltage = self.base_voltage + signal + random_noise

        # 电压不应为负数，因此低于 0V 时钳制为 0V。
        if voltage < 0:
            voltage = 0.0

        return voltage
