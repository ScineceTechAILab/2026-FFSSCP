from dataclasses import dataclass


@dataclass
class HardwareConfig:
    mode: str = "mock"
    bus: int = 1
    address: str = "0x48"
    channel: int = 0
    gain: float = 4.096


@dataclass
class CollectConfig:
    count: int = 20
    interval: float = 0.5
    output_dir: str = "data/samples"
    file_prefix: str = "sample"


@dataclass
class TrainConfig:
    data_path: str = "data/samples"
    feature_col: str = "raw_value"
    delimiter: str = ","
    has_header: bool = True
    epochs: int = 200
    batch_size: int = 32
    lr: float = 1e-3
    seed: int = 42
    val_split: float = 0.2
    log_interval: int = 20
    device: str = "cpu"
    output_dir: str = "models/latest"


@dataclass
class PredictConfig:
    model_path: str = "models/latest/model.pt"
    feature_col: str = "raw_value"
    delimiter: str = ","
    has_header: bool = True
