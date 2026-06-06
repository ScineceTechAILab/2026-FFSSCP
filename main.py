import argparse

import torch

from train import TrainConfig, train_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a regression model for suspended solids concentration."
    )
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-samples", type=int, default=512)
    parser.add_argument("--noise-std", type=float, default=0.1)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--log-interval", type=int, default=20)
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--save-path", type=str, default="")
    parser.add_argument("--csv-path", type=str, default="")
    parser.add_argument("--csv-intensity-col", type=str, default="voltage_v")
    parser.add_argument("--csv-delimiter", type=str, default=",")
    parser.add_argument("--csv-has-header", action="store_true")
    return parser.parse_args()


def resolve_device(device: str) -> str:
    if device.lower() == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def main() -> None:
    args = parse_args()
    config = TrainConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        seed=args.seed,
        n_samples=args.n_samples,
        noise_std=args.noise_std,
        val_split=args.val_split,
        log_interval=args.log_interval,
        device=resolve_device(args.device),
        save_path=args.save_path,
        csv_path=args.csv_path,
        csv_intensity_col=args.csv_intensity_col,
        csv_delimiter=args.csv_delimiter,
        csv_has_header=args.csv_has_header,
    )

    model, history = train_model(config)
    final_train = history["train_loss"][-1]
    final_val = history["val_loss"][-1]
    print(
        f"Training finished. device={config.device} "
        f"train_loss={final_train:.6f} val_loss={final_val:.6f}"
    )


if __name__ == "__main__":
    main()
