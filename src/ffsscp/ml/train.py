import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split

from ffsscp.data.dataset import load_tensor_dataset
from ffsscp.ml.config import TrainConfig
from ffsscp.ml.model import Network


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_loaders(dataset: TensorDataset, batch_size: int, val_split: float) -> Tuple[DataLoader, DataLoader]:
    if len(dataset) < 1:
        raise ValueError("Dataset is empty")
    if not 0 <= val_split < 1:
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
    dataset = load_tensor_dataset(
        config.data_path,
        config.feature_col,
        config.delimiter,
        config.has_header,
        device,
    )
    train_loader, val_loader = build_loaders(dataset, config.batch_size, config.val_split)

    model = Network().to(device)
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    history = {"train_loss": [], "val_loss": []}
    best_val = float("inf")
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.pt"

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

        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), str(model_path))

        if config.log_interval and epoch % config.log_interval == 0:
            print("Epoch {:03d}/{} train={:.6f} val={:.6f}".format(epoch, config.epochs, train_loss, val_loss))

    (output_dir / "train_config.json").write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")
    (output_dir / "metrics.json").write_text(
        json.dumps(
            {
                "final_train_loss": history["train_loss"][-1],
                "final_val_loss": history["val_loss"][-1],
                "best_val_loss": best_val,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return model, history
