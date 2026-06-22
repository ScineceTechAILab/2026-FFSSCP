# 2026-FFSSCP

本仓库用于存放“基于机器学习、光散射法的压裂反排液悬浮物浓度预测”项目中硬件驱动、数据收集、机器学习模型训练与预测代码。

本仓库主要负责：


项目英文缩写：

```text
FFSSCP = Fracturing Flowback Fluid Suspended Solids Concentration Prediction
```
---

## 软件环境

当前开发环境：

| 项目 | 版本/说明 |
|---|---|
| 系统平台 | Jetson Xavier NX 8GB |
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
2026-FFSSCP/
├─ main.py                         # 项目统一入口，启动交互式主菜单
├─ README.md
├─ requirements.txt
├─ .gitignore
│
├─ config/
│  └─ train.yaml                   # 采集、训练、预测配置
│
├─ data/
│  └─ samples/                     # 采集生成的样本数据
│     ├─ sample_YYYYMMDD_HHMMSS.csv
│     └─ sample_YYYYMMDD_HHMMSS.txt
│
├─ models/
│  └─ latest/                      # 最新训练产物
│     ├─ model.pt
│     ├─ train_config.json
│     └─ metrics.json
│
├─ src/
│  └─ ffsscp/
│     ├─ __init__.py
│     │
│     ├─ hardware/                 # 硬件层：传感器 / ADC / 采样
│     │  ├─ __init__.py
│     │  ├─ ads1115.py             # ADS1115 驱动与原始值读取
│     │  ├─ opt101.py              # OPT101 传感器封装
│     │  ├─ mock_sensor.py         # 无硬件环境下的模拟传感器
│     │  └─ sampler.py             # 统一采样流程
│     │
│     ├─ data/                     # 数据层：记录 / 标签 / 数据集 / 特征
│     │  ├─ __init__.py
│     │  ├─ schema.py              # CSV 字段定义
│     │  ├─ recording.py           # CSV / TXT 保存
│     │  ├─ features.py            # 特征提取逻辑（默认使用 raw_value）
│     │  └─ dataset.py             # 训练数据集加载
│     │
│     ├─ ml/                       # 模型层：训练 / 评估 / 推理
│     │  ├─ __init__.py
│     │  ├─ config.py              # 训练与预测配置数据结构
│     │  ├─ model.py               # 神经网络模型定义
│     │  ├─ train.py               # 模型训练逻辑
│     │  └─ predict.py             # 模型预测逻辑
│     │
│     └─ app/                      # 应用层：CLI 与主流程编排
│        ├─ __init__.py
│        ├─ config_loader.py       # 配置文件加载
│        ├─ flows.py               # 采集 / 训练 / 预测流程编排
│        └─ main.py                # 交互式菜单入口
│
├─ hardware-driver/                # 旧硬件项目（待迁移/清理）
└─ machine-learning/               # 旧机器学习项目（待迁移/清理）
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
