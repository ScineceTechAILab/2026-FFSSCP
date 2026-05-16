#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import time
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ffsscp_hardware.ads1115 import ADS1115Reader
from ffsscp_hardware.mock_sensor import MockLightSensor
from ffsscp_hardware.opt101 import OPT101Sensor


def create_output_path(label, mode):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "opt101_{}_{}_{}.csv".format(mode, label, timestamp)
    data_dir = os.path.join(PROJECT_ROOT, "data")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return os.path.join(data_dir, filename)


def create_voltage_reader(args):
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
    voltage_reader = create_voltage_reader(args)
    sensor = OPT101Sensor(voltage_reader)
    output_path = create_output_path(args.label, args.mode)

    with open(output_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "timestamp",
            "sensor",
            "adc",
            "channel",
            "raw_value",
            "voltage_v",
            "label",
            "mode"
        ])

        print("Logging OPT101 data to:")
        print(output_path)

        count = 0

        try:
            while args.count <= 0 or count < args.count:
                timestamp = datetime.now().isoformat(timespec="milliseconds")

                if args.mode == "hardware":
                    sample = voltage_reader.read_sample(args.channel)
                    raw_value = sample["raw_value"]
                    voltage = sample["voltage_v"]
                    adc_name = sample["adc"]
                    channel_name = sample["channel"]
                else:
                    sample = sensor.read_sample()
                    raw_value = ""
                    voltage = sample["voltage_v"]
                    adc_name = "mock"
                    channel_name = "A{}".format(args.channel)

                writer.writerow([
                    timestamp,
                    "OPT101",
                    adc_name,
                    channel_name,
                    raw_value,
                    "{:.6f}".format(voltage),
                    args.label,
                    args.mode
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
            if hasattr(voltage_reader, "close"):
                voltage_reader.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Log OPT101 light sensor data to CSV."
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "hardware"],
        default="mock",
        help="Data source mode."
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
        help="ADS1115 channel for hardware mode."
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
