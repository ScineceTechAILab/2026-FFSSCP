from pathlib import Path

import torch

from ffsscp.data.recording import build_sample_stem, ensure_dir, write_label_txt, write_sample_csv
from ffsscp.hardware.sampler import collect_samples, create_sensor
from ffsscp.ml.predict import predict_from_csv
from ffsscp.ml.train import train_model


def resolve_device(device: str) -> str:
    if device.lower() == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def run_collect(hardware_config, collect_config, concentration: float):
    # 读取配置中的样本输出目录
    output_dir = Path(collect_config.output_dir)
    # 如果目录不存在则自动创建，避免后续写文件时报错
    ensure_dir(output_dir)
    # 生成本次采样的文件主名，例如 sample_20260620_170000
    stem = build_sample_stem(output_dir, collect_config.file_prefix)
    # 生成本次采样对应的 CSV 路径，保存原始采样数据
    csv_path = stem.with_suffix(".csv")
    # 生成与 CSV 同名的 TXT 路径，用于保存该样本的浓度标签
    txt_path = stem.with_suffix(".txt")

    # 根据配置创建采样传感器对象：可以是 mock，也可以是真实硬件
    sensor = create_sensor(
        hardware_config.mode,
        hardware_config.bus,
        hardware_config.address,
        hardware_config.channel,
        hardware_config.gain,
    )
    reader = getattr(sensor, "reader", None)
    try:
        # 按配置循环采样 count 次，每次间隔 interval 秒
        # 返回值 rows 是一个列表，其中每个元素都是一条采样记录
        rows = collect_samples(sensor, collect_config.count, collect_config.interval, hardware_config.mode)
    finally:
        # 如果底层 reader 支持 close()，则在结束时关闭设备连接
        if reader is not None and hasattr(reader, "close"):
            reader.close()

    # 将本次采样得到的全部记录写入 CSV 文件
    write_sample_csv(csv_path, rows)
    # 将用户输入的悬浮物浓度写入同名 TXT，作为监督学习标签
    write_label_txt(txt_path, concentration)
    # 返回本次生成的 CSV 与 TXT 文件路径，供上层流程打印或后续处理
    return csv_path, txt_path


def run_train(train_config):
    train_config.device = resolve_device(train_config.device)
    return train_model(train_config)


def run_predict_from_csv(csv_path: str, predict_config, device: str = "cpu") -> float:
    return predict_from_csv(
        csv_path=csv_path,
        model_path=predict_config.model_path,
        feature_col=predict_config.feature_col,
        delimiter=predict_config.delimiter,
        has_header=predict_config.has_header,
        device=resolve_device(device),
    )


def run_predict_from_live(hardware_config, collect_config, predict_config, device: str = "cpu"):
    output_dir = Path(collect_config.output_dir)
    ensure_dir(output_dir)
    stem = build_sample_stem(output_dir, "predict")
    csv_path = stem.with_suffix(".csv")

    sensor = create_sensor(
        hardware_config.mode,
        hardware_config.bus,
        hardware_config.address,
        hardware_config.channel,
        hardware_config.gain,
    )
    reader = getattr(sensor, "reader", None)
    try:
        rows = collect_samples(sensor, collect_config.count, collect_config.interval, hardware_config.mode)
    finally:
        if reader is not None and hasattr(reader, "close"):
            reader.close()

    write_sample_csv(csv_path, rows)
    prediction = run_predict_from_csv(str(csv_path), predict_config, device)
    return csv_path, prediction

