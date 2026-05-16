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

from ffsscp_hardware.mock_sensor import MockLightSensor
from ffsscp_hardware.opt101 import OPT101Sensor


def create_output_path(label):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "opt101_{}_{}.csv".format(label, timestamp)
    data_dir = os.path.join(PROJECT_ROOT, "data")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    return os.path.join(data_dir, filename)


def log_csv(label, interval_seconds, sample_count):
    voltage_reader = MockLightSensor()
    sensor = OPT101Sensor(voltage_reader)
    output_path = create_output_path(label)

    with open(output_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            "timestamp",
            "sensor",
            "channel",
            "voltage_v",
            "label",
            "mode"
        ])

        print("Logging mock OPT101 data to:")
        print(output_path)

        count = 0

        while sample_count <= 0 or count < sample_count:
            timestamp = datetime.now().isoformat(timespec="milliseconds")
            sample = sensor.read_sample()
            voltage = sample["voltage_v"]

            writer.writerow([
                timestamp,
                "OPT101",
                "A0",
                "{:.6f}".format(voltage),
                label,
                "mock"
            ])
            csv_file.flush()

            print("{}, voltage={:.6f} V, label={}".format(
                timestamp,
                voltage,
                label
            ))

            count += 1
            time.sleep(interval_seconds)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Log OPT101 light sensor data to CSV."
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

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    log_csv(args.label, args.interval, args.count)
