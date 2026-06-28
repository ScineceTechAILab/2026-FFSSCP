from pathlib import Path

from ffsscp.ml.config import CollectConfig, HardwareConfig, PredictConfig, TrainConfig


# 将 YAML 中的标量字符串转成 Python 基本类型，
# 例如 true -> bool，0.5 -> float，20 -> int。
def _parse_scalar(value: str):
    text = value.split("#", 1)[0].strip()
    if not text:
        return ""
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text.strip('"').strip("'")


# 读取YAML 配置文件。
# 当前仅支持“section -> key: value”的两层结构，已足够覆盖本项目配置需求。
def load_simple_yaml(path: str) -> dict:
    result = {}
    current_section = None
    for raw_line in Path(path).read_text(encoding="utf-8-sig").splitlines():
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


# 将原始字典配置进一步映射为 dataclass，
# 方便后续在 app / ml 流程中用点号方式访问字段。
def load_configs(path: str):
    raw = load_simple_yaml(path)
    hardware = HardwareConfig(**raw.get("hardware", {}))
    collect = CollectConfig(**raw.get("collect", {}))
    train = TrainConfig(**raw.get("train", {}))
    predict = PredictConfig(**raw.get("predict", {}))
    return hardware, collect, train, predict
