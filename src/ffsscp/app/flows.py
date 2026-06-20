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
    output_dir = Path(collect_config.output_dir)
    ensure_dir(output_dir)
    stem = build_sample_stem(output_dir, collect_config.file_prefix)
    csv_path = stem.with_suffix(".csv")
    txt_path = stem.with_suffix(".txt")

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
    write_label_txt(txt_path, concentration)
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
