import time
from datetime import datetime
from typing import Dict, List

from ffsscp.hardware.ads1115 import ADS1115Reader
from ffsscp.hardware.mock_sensor import MockLightSensor
from ffsscp.hardware.opt101 import OPT101Sensor


# 根据运行模式创建统一的 OPT101 传感器对象。
# mock 模式下接入模拟传感器；hardware 模式下接入 ADS1115 实际硬件。
def create_sensor(mode: str, bus: int = 1, address: str = "0x48", channel: int = 0, gain: float = 4.096) -> OPT101Sensor:
    if mode == "mock":
        return OPT101Sensor(MockLightSensor())
    if mode == "hardware":
        reader = ADS1115Reader(
            bus_number=bus,
            address=int(address, 16),
            gain=gain,
            channel=channel,
        )
        return OPT101Sensor(reader)
    raise ValueError("Unsupported mode: {}".format(mode))


# 循环采样 count 次，每次采样间隔 interval 秒。
# 返回值 rows 是一个列表，每个元素代表一条完整采样记录，
# 后续会由 data 层统一写入 CSV 文件。
def collect_samples(sensor: OPT101Sensor, count: int, interval: float, mode: str) -> List[Dict[str, object]]:
    rows = []
    for index in range(1, count + 1):
        # 从传感器对象读取一条样本，包含 raw_value 和 voltage_v 等字段
        sample = sensor.read_sample()
        rows.append(
            {
                # 记录当前采样时间，便于后续追踪采样顺序和时间窗口
                "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                # 标记当前传感器类型，当前项目固定为 OPT101
                "sensor": "OPT101",
                # 标记当前 ADC 来源：mock 或 ADS1115
                "adc": sample.get("adc", mode),
                # 标记当前输入通道，例如 A0
                "channel": sample.get("channel", "A0"),
                # 标记当前采样模式，便于区分 mock 和真实硬件数据
                "mode": mode,
                # 标记这是本次采样中的第几条记录
                "sample_index": index,
                # 原始 ADC 值，后续训练与预测默认使用该字段
                "raw_value": sample["raw_value"],
                # 为调试和人工理解保留的电压值
                "voltage_v": sample["voltage_v"],
            }
        )
        # 最后一次采样后不再等待，避免多余的 sleep
        if index < count:
            time.sleep(interval)
    return rows
