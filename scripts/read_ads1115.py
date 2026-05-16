#!/usr/bin/env python3

import argparse
import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from ffsscp_hardware.ads1115 import ADS1115Reader


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read ADS1115 single-ended voltage."
    )
    parser.add_argument(
        "--bus",
        type=int,
        default=1,
        help="I2C bus number."
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
        help="ADS1115 input channel."
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
    address = int(args.address, 16)

    reader = ADS1115Reader(
        bus_number=args.bus,
        address=address,
        gain=args.gain
    )

    count = 0

    try:
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
        reader.close()
