from pathlib import Path

from ffsscp.ml.config import CollectConfig, HardwareConfig, PredictConfig, TrainConfig


def _parse_scalar(value: str):
    text = value.strip()
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text.strip('"').strip("'")


def load_simple_yaml(path: str) -> dict:
    result = {}
    current_section = None
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_section = line[:-1].strip()
            result[current_section] = {}
            continue
        if ":" not in line or current_section is None:
            continue
        key, value = line.strip().split(":", 1)
        result[current_section][key.strip()] = _parse_scalar(value)
    return result


def load_configs(path: str):
    raw = load_simple_yaml(path)
    hardware = HardwareConfig(**raw.get("hardware", {}))
    collect = CollectConfig(**raw.get("collect", {}))
    train = TrainConfig(**raw.get("train", {}))
    predict = PredictConfig(**raw.get("predict", {}))
    return hardware, collect, train, predict
