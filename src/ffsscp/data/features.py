from pathlib import Path

import numpy as np


# 判断传入列标识是否是整数字符串，
# 便于同时支持“按列名读取”和“按列索引读取”两种方式。
def _is_int_string(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


# 从单个 CSV 文件中读取指定特征列，并计算该列均值。
# 当前项目默认使用 raw_value 的均值作为模型输入特征。
def read_feature_mean(csv_path: Path, feature_col: str, delimiter: str = ",", has_header: bool = True) -> float:
    # 只要 feature_col 不是整数索引，就默认按带表头的 CSV 读取
    use_header = has_header or not _is_int_string(feature_col)
    if use_header:
        data = np.genfromtxt(str(csv_path), delimiter=delimiter, names=True, dtype=None, encoding="utf-8")
        names = data.dtype.names
        if not names:
            raise ValueError("CSV header was not found: %s" % csv_path)
        if _is_int_string(feature_col):
            col_index = int(feature_col)
            if col_index < 0:
                col_index = len(names) + col_index
            col_name = names[col_index]
        else:
            if feature_col not in names:
                raise ValueError("Feature column %s not found in %s" % (feature_col, csv_path))
            col_name = feature_col
        values = np.asarray(data[col_name], dtype=np.float64)
    else:
        data = np.genfromtxt(str(csv_path), delimiter=delimiter)
        if data.ndim == 1:
            data = np.expand_dims(data, 0)
        col_index = int(feature_col)
        if col_index < 0:
            col_index = data.shape[1] + col_index
        values = np.asarray(data[:, col_index], dtype=np.float64)

    # 过滤非数值与空值，避免错误数据影响特征计算
    values = np.atleast_1d(values)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("Feature column has no valid numeric values: %s" % csv_path)
    return float(values.mean())
