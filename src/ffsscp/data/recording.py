import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from ffsscp.data.schema import CSV_HEADERS


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_sample_stem(output_dir: Path, prefix: str = "sample") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / "{}_{}".format(prefix, timestamp)


def write_sample_csv(csv_path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_label_txt(txt_path: Path, concentration: float) -> None:
    txt_path.write_text("{}\n".format(concentration), encoding="utf-8")
