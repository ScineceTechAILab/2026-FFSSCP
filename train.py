import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split

from src.core.layers import Network


@dataclass
class TrainConfig:
    epochs: int = 200
    batch_size: int = 32
    lr: float = 1e-3
    seed: int = 42
    n_samples: int = 512
    noise_std: float = 0.1
    val_split: float = 0.2
    log_interval: int = 20
    device: str = "cpu"
    save_path: str = ""
    csv_path: str = ""
    csv_intensity_col: str = "voltage_v"
    csv_delimiter: str = ","
    csv_has_header: bool = False


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def make_synthetic_dataset(
    n_samples: int, noise_std: float, device: torch.device
) -> TensorDataset:
    x = torch.linspace(-1.0, 1.0, n_samples, device=device).unsqueeze(1)
    noise = torch.randn_like(x) * noise_std
    y = 3.0 * x + 0.5 + noise
    return TensorDataset(x, y)


def _is_int_string(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def _read_target_from_txt(csv_path: Path) -> float:
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


def _read_intensity_mean(
    csv_path: Path,
    intensity_col: str,
    delimiter: str,
    has_header: bool,
) -> float:
    if not csv_path.is_file():
        raise FileNotFoundError("CSV file not found: %s" % csv_path)

    use_header = has_header or not _is_int_string(intensity_col)
    if use_header:
        data = np.genfromtxt(
            str(csv_path), delimiter=delimiter, names=True, dtype=None, encoding="utf-8"
        )
        names = data.dtype.names
        if not names:
            raise ValueError("CSV header was not found: %s" % csv_path)
        if _is_int_string(intensity_col):
            col_index = int(intensity_col)
            if col_index < 0:
                col_index = len(names) + col_index
            if col_index < 0 or col_index >= len(names):
                raise ValueError("csv_intensity_col is out of range: %s" % csv_path)
            col_name = names[col_index]
        else:
            if intensity_col not in names:
                raise ValueError(
                    "Intensity column %s not found in %s. Available columns: %s"
                    % (intensity_col, csv_path, ", ".join(names))
                )
            col_name = intensity_col
        values = np.asarray(data[col_name], dtype=np.float64)
    else:
        data = np.genfromtxt(str(csv_path), delimiter=delimiter)
        if data.ndim == 1:
            data = np.expand_dims(data, 0)
        col_index = int(intensity_col)
        if col_index < 0:
            col_index = data.shape[1] + col_index
        if col_index < 0 or col_index >= data.shape[1]:
            raise ValueError("csv_intensity_col is out of range: %s" % csv_path)
        values = np.asarray(data[:, col_index], dtype=np.float64)

    values = np.atleast_1d(values)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("Intensity column has no valid numeric values: %s" % csv_path)
    return float(values.mean())


def load_csv_dataset(
    csv_path: str,
    intensity_col: str,
    delimiter: str,
    has_header: bool,
    device: torch.device,
) -> TensorDataset:
    path = Path(csv_path)
    if path.is_dir():
        csv_files = sorted(path.glob("*.csv"))
    elif path.is_file():
        csv_files = [path]
    else:
        raise FileNotFoundError("CSV file or directory not found: %s" % csv_path)

    if not csv_files:
        raise ValueError("No CSV files found: %s" % csv_path)

    features = []
    targets = []
    for current_csv in csv_files:
        features.append(_read_intensity_mean(current_csv, intensity_col, delimiter, has_header))
        targets.append(_read_target_from_txt(current_csv))

    x = np.asarray(features, dtype=np.float32).reshape(-1, 1)
    y = np.asarray(targets, dtype=np.float32).reshape(-1, 1)
    x_tensor = torch.tensor(x, dtype=torch.float32, device=device)
    y_tensor = torch.tensor(y, dtype=torch.float32, device=device)
    return TensorDataset(x_tensor, y_tensor)


def build_loaders(
    dataset: TensorDataset, batch_size: int, val_split: float
) -> Tuple[DataLoader, DataLoader]:
    if len(dataset) < 1:
        raise ValueError("Dataset is empty")
    if val_split < 0 or val_split >= 1:
        raise ValueError("val_split must be in [0, 1)")

    val_size = int(len(dataset) * val_split)
    train_size = len(dataset) - val_size
    train_set, val_set = random_split(dataset, [train_size, val_size])
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader


def evaluate(model: nn.Module, loader: DataLoader, loss_fn: nn.Module) -> float:
    model.eval()
    total_loss = 0.0
    count = 0
    with torch.no_grad():
        for x, y in loader:
            preds = model(x)
            loss = loss_fn(preds, y)
            total_loss += loss.item() * x.size(0)
            count += x.size(0)
    return total_loss / max(count, 1)


def train_model(config: TrainConfig) -> Tuple[nn.Module, Dict[str, list]]:
    device = torch.device(config.device)
    set_seed(config.seed)

    if not config.csv_path:
        raise ValueError("csv_path is required")
    dataset = load_csv_dataset(
        config.csv_path,
        config.csv_intensity_col,
        config.csv_delimiter,
        config.csv_has_header,
        device,
    )
    train_loader, val_loader = build_loaders(
        dataset, config.batch_size, config.val_split
    )

    model = Network().to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    history = {"train_loss": [], "val_loss": []}
    best_val = float("inf")

    for epoch in range(1, config.epochs + 1):
        model.train()
        running_loss = 0.0
        count = 0
        for x, y in train_loader:
            optimizer.zero_grad()
            preds = model(x)
            loss = loss_fn(preds, y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * x.size(0)
            count += x.size(0)

        train_loss = running_loss / max(count, 1)
        val_loss = evaluate(model, val_loader, loss_fn)
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)

        if config.save_path and val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), config.save_path)

        if config.log_interval and epoch % config.log_interval == 0:
            print(
                f"Epoch {epoch:03d}/{config.epochs} "
                f"train={train_loss:.6f} val={val_loss:.6f}"
            )

    return model, history
