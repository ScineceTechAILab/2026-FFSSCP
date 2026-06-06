# 2026-FFSSCP_Hardware_Driver

本仓库用于存放“基于机器学习、光散射法的压裂反排液悬浮物浓度预测”项目中的机器学习训练以及预测代码。

本仓库主要负责：

- 提供训练脚本与示例模型结构


项目英文缩写：

```text
FFSSCP = Fracturing Flowback Fluid Suspended Solids Concentration Prediction
```

---

## 软件环境

当前开发环境：

| 项目 | 版本/说明 |
|---|---|
| 系统平台 | Jetson Nano 2GB |
| Python | Python 3.6.9 |
| Git 分支 | main |

查看 Python 版本：

```bash
python3 --version
```


说明：

- 本项目统一使用 `python3` 运行脚本。
- 不建议修改 `/usr/bin/python` 指向，避免影响系统组件。
- 当前代码兼容 Jetson Nano 常见的 Python 3.6 环境。

---

## 项目结构

```text
2026-FFSSCP_Machine_Learning/
├── README.md
├── requirements.txt
├── docs/
│   └── 
├── src/
│   └── core/
│       ├── layers.py
│       └── 
├── train.py
├── main.py
```

目录说明：

| 目录/文件                  | 说明 |
|------------------------|---|
| `main.py`               | 可直接运行的命令行脚本 |
| `train.py`              | 训练逻辑与数据构造 |
| `src/core/layers.py`    | 模型结构定义 |
| `requirements.txt`     | Python 依赖说明 |

---

## 使用方法

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```


训练示例（使用 CSV 数据）：

```bash
python3 main.py --csv-path ./data.csv --csv-target-col -1 --csv-has-header
```

CSV 说明：

- 至少包含 2 列：特征列 + 目标列。
- 目标列用 `--csv-target-col` 指定，默认 `-1` 表示最后一列。
- 当前 `Network` 仅支持 1 维输入，请确保只有 1 列特征。
- 分隔符默认 `,`，可用 `--csv-delimiter` 指定。

常用参数：

- `--device auto|cpu|cuda` 自动或指定设备
- `--save-path ./model.pt` 保存最佳验证集模型
- `--csv-path ./data.csv` CSV 文件路径
- `--csv-target-col -1` 目标列索引
- `--csv-delimiter ,` CSV 分隔符
- `--csv-has-header` CSV 是否有表头

输出说明：

- 终端打印每 `log-interval` 个 epoch 的训练/验证损失
- 训练结束打印最终损失

---

## Git 提交规范

本项目使用以下提交格式：

```text
type(scope): 中文描述
```

示例：

```text
feat(adc): 添加ADS1115硬件读取接口
feat(sensor): 添加OPT101模拟采集与CSV记录
docs(code): 添加硬件采集代码注释
docs(wiring): 添加Jetson Nano IO引脚说明图
```

常用类型：

| 类型 | 含义 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修复问题 |
| `docs` | 文档 |
| `chore` | 初始化、配置、杂项 |
| `test` | 测试 |
| `refactor` | 重构 |

---
