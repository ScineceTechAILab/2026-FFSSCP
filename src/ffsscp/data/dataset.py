from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from torch.utils.data import TensorDataset

from ffsscp.data.features import read_feature_mean


# 读取与 CSV 同名的 TXT 标签文件。
# 该 TXT 中保存悬浮物浓度，作为监督学习的目标值。
def read_target_from_txt(csv_path: Path) -> float:
    txt_path = csv_path.with_suffix(".txt")
    if not txt_path.is_file():
        raise FileNotFoundError("Matching concentration TXT not found: %s" % txt_path)
    content = txt_path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("Concentration TXT is empty: %s" % txt_path)
    for token in content.replace(",", " ").split():
        try:
            return float(token)
        except ValueError:
            continue
    raise ValueError("No numeric concentration found in TXT: %s" % txt_path)


# 列出数据目录中的全部样本 CSV 文件。
# 支持传入单个 CSV 文件路径，也支持传入包含多个样本的目录路径。
def list_sample_csv_files(data_path: str) -> List[Path]:
    path = Path(data_path)
    if path.is_dir():
        return sorted(path.glob("*.csv"))
    if path.is_file():
        return [path]
    raise FileNotFoundError("CSV file or directory not found: %s" % data_path)


# 从一个样本目录中加载全部训练数组。
# 每个 CSV 提取一个特征值，每个同名 TXT 提取一个目标值。
def load_training_arrays(data_path: str, feature_col: str, delimiter: str, has_header: bool) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, object]]]:
    csv_files = list_sample_csv_files(data_path)
    if not csv_files:
        raise ValueError("No CSV files found: %s" % data_path)

    features = []
    targets = []
    metadata = []
    for csv_file in csv_files:
        feature = read_feature_mean(csv_file, feature_col, delimiter, has_header)
        target = read_target_from_txt(csv_file)
        features.append(feature)
        targets.append(target)
        # metadata 方便后续调试、排查异常样本与扩展分析逻辑
        metadata.append({"csv_path": str(csv_file), "target": target, "feature": feature})

    x = np.asarray(features, dtype=np.float32).reshape(-1, 1)
    y = np.asarray(targets, dtype=np.float32).reshape(-1, 1)
    return x, y, metadata


# 将 numpy 数组进一步转换为 PyTorch 可直接训练的 TensorDataset。
def load_tensor_dataset(data_path: str, feature_col: str, delimiter: str, has_header: bool, device: torch.device) -> TensorDataset:
    x, y, _ = load_training_arrays(data_path, feature_col, delimiter, has_header)
    x_tensor = torch.tensor(x, dtype=torch.float32, device=device)
    y_tensor = torch.tensor(y, dtype=torch.float32, device=device)
    return TensorDataset(x_tensor, y_tensor)
