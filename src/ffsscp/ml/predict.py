from pathlib import Path

import torch

from ffsscp.data.features import read_feature_mean
from ffsscp.ml.model import Network


def load_model(model_path: str, device: str = "cpu") -> Network:
    model = Network().to(torch.device(device))
    state_dict = torch.load(model_path, map_location=torch.device(device))
    model.load_state_dict(state_dict)
    model.eval()
    return model


def predict_from_csv(
    csv_path: str,
    model_path: str,
    feature_col: str = "raw_value",
    delimiter: str = ",",
    has_header: bool = True,
    device: str = "cpu",
) -> float:
    feature = read_feature_mean(Path(csv_path), feature_col, delimiter, has_header)
    model = load_model(model_path, device)
    x = torch.tensor([[feature]], dtype=torch.float32, device=torch.device(device))
    with torch.no_grad():
        prediction = model(x).item()
    return float(prediction)
