import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping

from ffsscp.data.schema import CSV_HEADERS


# 确保输出目录存在；如果不存在则递归创建。
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# 为本次采样生成文件主名，例如 sample_20260620_173000。
# 返回的 stem 不包含扩展名，后续可派生出 .csv 和 .txt 两个文件。
def build_sample_stem(output_dir: Path, prefix: str = "sample") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / "{}_{}".format(prefix, timestamp)


# 将一批采样记录写入 CSV 文件。
# rows 中每个元素都应当符合 schema.py 中定义的字段结构。
def write_sample_csv(csv_path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# 将用户输入的悬浮物浓度写入同名 TXT 文件。
# 该文件作为监督学习标签，与对应 CSV 构成一个完整训练样本。
def write_label_txt(txt_path: Path, concentration: float) -> None:
    txt_path.write_text("{}\n".format(concentration), encoding="utf-8")
