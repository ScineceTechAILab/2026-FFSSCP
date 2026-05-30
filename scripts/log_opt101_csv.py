#!/usr/bin/env python3
"""
OPT101 数据采集与 CSV 记录脚本。

本脚本用于采集 OPT101 光电传感器输出电压，并保存为 CSV 文件。

支持两种采集模式：
1. mock：无硬件时生成模拟电压，用于测试采集流程；
2. hardware：通过 ADS1115 读取 OPT101 的真实输出电压。

CSV 文件默认保存到项目 data/ 目录。
由于 data/*.csv 已写入 .gitignore，采集数据默认不会提交到 GitHub。

示例:
    python3 scripts/log_opt101_csv.py --mode mock --label normal --count 20
    python3 scripts/log_opt101_csv.py --mode hardware --label normal --bus 1 --address 0x48 --channel 0 --count 20
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime

# 将项目 src 目录加入 Python 搜索路径，便于直接从 scripts 目录运行。
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ffsscp_hardware.ads1115 import ADS1115Reader
from ffsscp_hardware.mock_sensor import MockLightSensor
from ffsscp_hardware.opt101 import OPT101Sensor


def create_output_path(label, mode):
    """
    根据采集模式、标签和当前时间生成 CSV 输出路径。

    文件名示例:
        opt101_hardware_normal_20260516_010900.csv
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "opt101_{}_{}_{}.csv".format(mode, label, timestamp)
    data_dir = os.path.join(PROJECT_ROOT, "data")

    # 如果 data 目录不存在，则自动创建。
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return os.path.join(data_dir, filename)


def create_voltage_reader(args):
    """
    根据采集模式创建电压读取对象。

    mock 模式:
        使用 MockLightSensor 生成模拟电压。

    hardware 模式:
        使用 ADS1115Reader 通过 I2C 读取真实电压。
    """
    if args.mode == "mock":
        return MockLightSensor()

    if args.mode == "hardware":
        address = int(args.address, 16)
        return ADS1115Reader(
            bus_number=args.bus,
            address=address,
            gain=args.gain
        )

    raise ValueError("Unsupported mode: {}".format(args.mode))


def log_csv(args):
    """
    执行 OPT101 数据采集并写入 CSV。

    每条数据包含：
    - timestamp: 采样时间；
    - sensor: 传感器名称；
    - adc: ADC 名称或 mock；
    - channel: ADS1115 输入通道；
    - raw_value: ADS1115 原始值，mock 模式下为空；
    - voltage_v: 电压值，单位 V；
    - label: 样本标签；
    - mode: 采集模式。
    """
    voltage_reader = create_voltage_reader(args)
    sensor = OPT101Sensor(voltage_reader)
    output_path = create_output_path(args.label, args.mode)

    with open(output_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        # CSV 表头，后续机器学习处理时可按这些字段读取。
        writer.writerow([
            "timestamp",
            "sensor",
            "adc",
            "channel",
            "mode",
            "label",
            "sample_index",
            "raw_value",
            "voltage_v"
        ])

        print("Logging OPT101 data to:")
        print(output_path)

        count = 0

        try:
            # 主采集循环：按 interval 间隔采样，count 为 0 时持续采集。
            while args.count <= 0 or count < args.count:
                timestamp = datetime.now().isoformat(timespec="milliseconds")

                if args.mode == "hardware":
                    # 硬件模式：从 ADS1115 获取 raw_value 和 voltage_v。
                    sample = voltage_reader.read_sample(args.channel)
                    raw_value = sample["raw_value"]
                    voltage = sample["voltage_v"]
                    adc_name = sample["adc"]
                    channel_name = sample["channel"]
                else:
                    # 模拟模式：只生成 voltage_v，raw_value 留空。
                    sample = sensor.read_sample()
                    raw_value = ""
                    voltage = sample["voltage_v"]
                    adc_name = "mock"
                    channel_name = "A{}".format(args.channel)

                sample_index = count + 1

                writer.writerow([
                    timestamp,
                    "OPT101",
                    adc_name,
                    channel_name,
                    args.mode,
                    args.label,
                    sample_index,
                    raw_value,
                    "{:.6f}".format(voltage)
                ])
                csv_file.flush()

                print(
                    "{}, mode={}, channel={}, raw={}, voltage={:.6f} V, label={}".format(
                        timestamp,
                        args.mode,
                        channel_name,
                        raw_value,
                        voltage,
                        args.label
                    )
                )

                count += 1
                time.sleep(args.interval)
        finally:
            # 如果底层读取器支持 close()，退出时关闭硬件资源。
            if hasattr(voltage_reader, "close"):
                voltage_reader.close()


def parse_args():
    """
    解析命令行参数。

    包括采集模式、标签、采样间隔、采样次数、
    I2C 总线、ADS1115 地址、输入通道和量程。
    """
    parser = argparse.ArgumentParser(
        description="Log OPT101 light sensor data to CSV."
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "hardware"],
        default="mock",
        help="Data source mode: mock or hardware."
    )
    parser.add_argument(
        "--label",
        default="unlabeled",
        help="Sample label, for example dark, normal, strong."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Sampling interval in seconds."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of samples. Use 0 for infinite logging."
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=1,
        help="I2C bus number for hardware mode."
    )
    parser.add_argument(
        "--address",
        default="0x48",
        help="ADS1115 I2C address for hardware mode."
    )
    parser.add_argument(
        "--channel",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="ADS1115 channel for hardware mode. 0~3 correspond to A0~A3."
    )
    parser.add_argument(
        "--gain",
        type=float,
        default=4.096,
        choices=[6.144, 4.096, 2.048, 1.024, 0.512, 0.256],
        help="ADS1115 full-scale voltage range."
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    log_csv(args)
