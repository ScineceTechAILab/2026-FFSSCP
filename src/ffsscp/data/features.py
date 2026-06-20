from pathlib import Path

import numpy as np


def _is_int_string(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def read_feature_mean(csv_path: Path, feature_col: str, delimiter: str = ",", has_header: bool = True) -> float:
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

    values = np.atleast_1d(values)
    values = values[np.isfinite(values)]
    if values.size == 0:
        raise ValueError("Feature column has no valid numeric values: %s" % csv_path)
    return float(values.mean())
