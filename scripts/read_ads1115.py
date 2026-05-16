#!/usr/bin/env python3
"""
ADS1115 实时读取测试脚本。

该脚本用于快速检查 ADS1115 是否能通过 I2C 正常读取电压。
适合在以下场景使用：
1. A0 接 GND，验证读数是否接近 0V；
2. A0 接 3.3V，验证读数是否接近 3.3V；
3. A0 接 OPT101 OUT，观察遮光和照光时电压是否变化。

示例:
    python3 scripts/read_ads1115.py --bus 1 --address 0x48 --channel 0 --count 10
"""

import argparse
import os
import sys
import time

# 将项目 src 目录加入 Python 搜索路径，便于直接从 scripts 目录运行。
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ffsscp_hardware.ads1115 import ADS1115Reader


def parse_args():
    """
    解析命令行参数。

    支持指定 I2C 总线、ADS1115 地址、输入通道、量程、
    采样间隔和采样次数。
    """
    parser = argparse.ArgumentParser(
        description="Read ADS1115 single-ended voltage."
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=1,
        help="I2C bus number. Jetson Nano 40-pin header usually uses bus 1."
    )
    parser.add_argument(
        "--address",
        default="0x48",
        help="ADS1115 I2C address, for example 0x48."
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="ADS1115 input channel. 0~3 correspond to A0~A3."
    )
    parser.add_argument(
        "--gain",
        type=float,
        default=4.096,
        choices=[6.144, 4.096, 2.048, 1.024, 0.512, 0.256],
        help="ADS1115 full-scale voltage range."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Read interval in seconds."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of samples. Use 0 for infinite."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 将命令行传入的十六进制地址字符串转换为整数，例如 "0x48" -> 72。
    address = int(args.address, 16)

    # 创建 ADS1115 读取器，后续通过它读取指定通道电压。
    reader = ADS1115Reader(
        bus_number=args.bus,
        address=address,
        gain=args.gain
    )

    count = 0

    try:
        # 循环读取电压；count 为 0 时表示持续读取，直到用户按 Ctrl+C 停止。
        while args.count <= 0 or count < args.count:
            sample = reader.read_sample(args.channel)
            print(
                "adc={adc}, channel={channel}, raw={raw_value}, voltage={voltage_v:.6f} V".format(
                    **sample
                )
            )
            count += 1
            time.sleep(args.interval)
    finally:
        # 程序退出前关闭 I2C 总线。
        reader.close()
