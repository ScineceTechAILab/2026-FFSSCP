#!/usr/bin/env python3
"""
I2C 设备扫描脚本。

本脚本调用系统工具 i2cdetect 扫描 I2C 总线。
在 Jetson Nano 2GB 上，ADS1115 接到 40Pin J6 排针的 I2C 后，
通常使用 bus 1，也就是 /dev/i2c-1。

当 ADS1115 的 ADDR 引脚接 GND 时，设备地址通常为 0x48。

示例:
    python3 scripts/i2c_scan.py --bus 1

等价于:
    i2cdetect -y -r 1
"""

import argparse
import subprocess


def run_i2cdetect(bus_number):
    """
    调用 i2cdetect 扫描指定 I2C 总线。

    参数:
        bus_number: I2C 总线编号，例如 1 对应 /dev/i2c-1。

    说明:
        -y 表示跳过交互确认；
        -r 表示使用 read 模式扫描。
    """
    # 等价于命令行执行：i2cdetect -y -r <bus_number>
    command = ["i2cdetect", "-y", "-r", str(bus_number)]
    subprocess.check_call(command)


def parse_args():
    """
    解析 I2C 总线编号参数。
    """
    parser = argparse.ArgumentParser(
        description="Scan I2C devices using i2cdetect."
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=1,
        help="I2C bus number. Jetson Nano 40-pin header usually uses bus 1."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_i2cdetect(args.bus)
