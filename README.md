# 2026-FFSSCP_Hardware_Driver

本仓库用于存放“基于机器学习、光散射法的压裂反排液悬浮物浓度预测”项目中的硬件驱动与数据采集代码。

本仓库主要负责：

- Jetson Nano 2GB 硬件采集环境搭建
- ADS1115 模数转换器 I2C 读取
- OPT101 光电传感器电压采集
- 光照/散射信号 CSV 数据记录
- 后续机器学习模型训练所需的原始数据采集

项目英文缩写：

```text
FFSSCP = Fracturing Flowback Fluid Suspended Solids Concentration Prediction
```

---

## 硬件组成

当前硬件采集链路为：

```text
OPT101 光电传感器
        ↓ 模拟电压
ADS1115 模数转换器
        ↓ I2C
Jetson Nano 2GB
        ↓ CSV
实验数据文件
```

主要硬件：

| 硬件 | 作用 |
|---|---|
| Jetson Nano 2GB | 运行 Python 采集程序 |
| ADS1115 | 将 OPT101 模拟电压转换为数字量 |
| OPT101 | 采集光照/散射信号并输出模拟电压 |
| 杜邦线 | 连接 Jetson、ADS1115 和 OPT101 |

---

## 软件环境

当前开发环境：

| 项目 | 版本/说明 |
|---|---|
| 系统平台 | Jetson Nano 2GB |
| Python | Python 3.6.9 |
| I2C 工具 | i2c-tools |
| Python I2C 库 | python3-smbus |
| Git 分支 | main |

查看 Python 版本：

```bash
python3 --version
```

安装硬件采集依赖：

```bash
sudo apt update
sudo apt install -y i2c-tools python3-smbus
```

说明：

- 本项目统一使用 `python3` 运行脚本。
- 不建议修改 `/usr/bin/python` 指向，避免影响系统组件。
- 当前代码兼容 Jetson Nano 常见的 Python 3.6 环境。

---

## 硬件接线

### ADS1115 与 Jetson Nano 2GB

ADS1115 接 Jetson Nano 2GB 的 40Pin J6 排针。

| ADS1115 | Jetson Nano 2GB |
|---|---|
| VDD | 3.3V |
| GND | GND |
| SDA | I2C SDA |
| SCL | I2C SCL |
| ADDR | GND |

常用物理引脚：

| 功能 | Jetson Nano 2GB 40Pin |
|---|---|
| 3.3V | Pin 1 |
| SDA | Pin 3 |
| SCL | Pin 5 |
| GND | Pin 6 |

当 `ADDR` 接 `GND` 时，ADS1115 的 I2C 地址为：

```text
0x48
```

接口说明图见：

```text
docs/J6-IO引脚图.png
```

### OPT101 与 ADS1115

OPT101 输出的是模拟电压，不能直接接 Jetson Nano GPIO。

正确接法：

| OPT101 | ADS1115 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| OUT | A0 |

注意：

- Jetson Nano 没有模拟输入，不能直接读取 OPT101 OUT。
- OPT101 OUT 必须先接入 ADS1115。
- ADS1115 使用 3.3V 供电时，A0 输入电压不要超过 3.3V。
- Jetson Nano I2C 为 3.3V 逻辑，避免使用 5V I2C 电平。

---

## 安全注意事项

接线前建议断电操作：

```text
断电 → 接线 → 检查 → 上电
```

注意事项：

- 不要将 5V 接入 ADS1115 A0。
- 不要将 5V 接入 Jetson Nano GPIO 或 I2C 信号脚。
- 不要将 OPT101 OUT 直接接 Jetson Nano GPIO。
- Jetson、ADS1115、OPT101 必须共地。
- 如果 SDA 和 SCL 接反，通常表现为扫描不到 `0x48`。

---

## 项目结构

```text
2026-FFSSCP_Hardware_Driver/
├── README.md
├── requirements.txt
├── docs/
│   └── xx.png
├── scripts/
│   ├── i2c_scan.py
│   ├── read_ads1115.py
│   └── log_opt101_csv.py
├── src/
│   └── ffsscp_hardware/
│       ├── __init__.py
│       ├── ads1115.py
│       ├── mock_sensor.py
│       └── opt101.py
├── data/
│   └── .gitkeep
└── tests/
```

目录说明：

| 目录/文件 | 说明 |
|---|---|
| `scripts/` | 可直接运行的命令行脚本 |
| `src/ffsscp_hardware/` | 硬件采集核心模块 |
| `docs/` | 接线图和说明资料 |
| `data/` | 本地采集 CSV 数据 |
| `requirements.txt` | Python 依赖说明 |

---

## 使用方法

### 1. 扫描 I2C 设备

使用项目脚本：

```bash
python3 scripts/i2c_scan.py --bus 1
```

或直接使用系统命令：

```bash
sudo i2cdetect -y -r 1
```

如果 ADS1115 接线正确，应看到地址：

```text
0x48
```

---

### 2. 实时读取 ADS1115 电压

读取 A0 通道：

```bash
python3 scripts/read_ads1115.py --bus 1 --address 0x48 --channel 0 --count 10
```

常见测试：

```text
A0 接 GND   → 电压约 0V
A0 接 3.3V  → 电压约 3.3V
A0 接 OPT101 OUT → 电压随光照变化
```

---

### 3. 模拟模式采集

无硬件时可以使用 mock 模式生成模拟数据：

```bash
python3 scripts/log_opt101_csv.py --mode mock --label normal --count 20
```

该模式用于测试 CSV 记录流程，不代表真实传感器数据。

---

### 4. 硬件模式采集 OPT101

正常环境光：

```bash
python3 scripts/log_opt101_csv.py --mode hardware --label normal --bus 1 --address 0x48 --channel 0 --count 100
```

遮光：

```bash
python3 scripts/log_opt101_csv.py --mode hardware --label dark --bus 1 --address 0x48 --channel 0 --count 100
```

强光：

```bash
python3 scripts/log_opt101_csv.py --mode hardware --label strong --bus 1 --address 0x48 --channel 0 --count 100
```

参数说明：

| 参数 | 说明 |
|---|---|
| `--mode` | 采集模式，`mock` 或 `hardware` |
| `--label` | 样本标签，例如 `dark`、`normal`、`strong` |
| `--bus` | I2C 总线编号，Jetson Nano 常用 `1` |
| `--address` | ADS1115 地址，默认 `0x48` |
| `--channel` | ADS1115 通道，A0 对应 `0` |
| `--count` | 采样数量，`0` 表示持续采集 |
| `--interval` | 采样间隔，单位秒 |
| `--gain` | ADS1115 满量程范围，默认 `4.096` |

---

## CSV 数据格式

采集数据默认保存到：

```text
data/
```

文件名示例：

```text
opt101_hardware_normal_20260516_010900.csv
```

CSV 字段：

| 字段 | 说明 |
|---|---|
| `timestamp` | 采样时间 |
| `sensor` | 传感器名称，当前为 `OPT101` |
| `adc` | ADC 名称，硬件模式为 `ADS1115` |
| `channel` | 输入通道，例如 `A0` |
| `mode` | 采集模式，`mock` 或 `hardware` |
| `label` | 样本标签 |
| `sample_index` | 样本序号，从 `1` 开始递增 |
| `raw_value` | ADS1115 原始 ADC 数值 |
| `voltage_v` | 换算后的电压值，单位 V |

示例：

```csv
timestamp,sensor,adc,channel,mode,label,sample_index,raw_value,voltage_v
2026-05-16T01:09:00.338,OPT101,ADS1115,A0,hardware,normal,1,26422,3.302750
```

---

## 数据文件管理

采集产生的 CSV 文件不会提交到 GitHub。

`.gitignore` 中已忽略：

```text
data/*.csv
__pycache__/
*.pyc
```

`data/.gitkeep` 用于保留 `data/` 目录结构。

---

## 当前验证结果

已完成以下硬件验证：

| 测试 | 结果 |
|---|---|
| I2C 扫描 | 识别到 ADS1115 地址 `0x48` |
| A0 接 GND | 读数接近 `0V` |
| A0 接 3.3V | 读数约 `3.302V` |
| 硬件 CSV 采集 | 可正常生成 CSV 文件 |

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
