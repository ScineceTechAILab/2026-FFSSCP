#!/usr/bin/env python3

import argparse
import subprocess


def run_i2cdetect(bus_number):
    command = ["i2cdetect", "-y", "-r", str(bus_number)]
    subprocess.check_call(command)


def parse_args():
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