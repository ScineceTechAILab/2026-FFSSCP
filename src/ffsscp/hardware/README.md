# 硬件接线说明

本文档只描述 `ffsscp.hardware` 这一层涉及的硬件连接与参数约定，便于从 Jetson Nano 2GB 切换到 Jetson Xavier NX 8GB 后继续使用同一套采集逻辑。

## 硬件结论

这套实现的硬件核心仍然是：

- Jetson Xavier NX 8GB 通过 I2C 连接 ADS1115
- ADS1115 负责把模拟信号转换成数字量
- OPT101 模块输出模拟信号，接到 ADS1115 的单端输入通道
- 软件侧默认读取 `A0` 通道，I2C 地址默认 `0x48`

如果你的 Xavier NX 使用的是官方 40-pin 扩展口，并且 I2C 走线与 Nano 时代一致，那么**代码层通常不需要因为换板而重写**。真正需要确认的是：I2C 总线号、引脚接法、供电电压和 ADC 地址跳线。

## 推荐接线

下表按常见 Jetson 40-pin 头和 ADS1115 / OPT101 模块的组合来写。不同载板如果针脚编号不同，请以载板手册为准。

| Jetson Xavier NX 8GB | 连接到 | 说明 |
|---|---|---|
| 3.3V 电源 | ADS1115 VDD | 供电建议使用 3.3V，保持 I2C 电平一致 |
| GND | ADS1115 GND | 必须共地 |
| I2C SDA | ADS1115 SDA | 数据线 |
| I2C SCL | ADS1115 SCL | 时钟线 |
| 3.3V 电源或模块供电脚 | OPT101 VCC / V+ | 视模块设计而定，优先保证输出不超过 ADS1115 输入范围 |
| GND | OPT101 GND | 必须共地 |
| OPT101 模拟输出 | ADS1115 A0 | 当前代码默认读 A0 单端输入 |

## I2C 地址与总线

当前项目的默认配置如下：

| 参数 | 默认值 | 含义 |
|---|---|---|
| `hardware.bus` | `1` | I2C 总线号 |
| `hardware.address` | `0x48` | ADS1115 默认地址 |
| `hardware.channel` | `0` | 读取 ADS1115 的 A0 |
| `hardware.gain` | `4.096` | ADS1115 满量程配置 |

ADS1115 的地址由 `ADDR` 引脚决定，常见配置如下：

| ADDR 连接 | I2C 地址 |
|---|---|
| 接 GND | `0x48` |
| 接 VDD | `0x49` |
| 接 SDA | `0x4A` |
| 接 SCL | `0x4B` |

当前代码里 `config/train.yaml` 的默认值仍然是 `bus=1`、`address=0x48`、`channel=0`、`gain=4.096`，和硬件层实现保持一致。

## 为什么换成 Xavier NX 后通常不用改代码

`src/ffsscp/hardware` 这一层做的是**I2C 读数抽象**，而不是绑定某一块 Jetson 板子的专用驱动。

在当前实现中：

- `ADS1115Reader` 只关心 I2C 总线、地址、通道和量程
- `OPT101Sensor` 只是把传感器读数统一成 `raw_value` / `voltage_v`
- `sampler.py` 只负责把采样数据整理成统一记录

因此，从 Jetson Nano 2GB 切到 Jetson Xavier NX 8GB，**如果 I2C 接线、供电和总线号不变，硬件代码通常可以直接复用**。

## 需要重点检查的地方

1. **I2C 总线是否还是 `1`**  
   默认代码写的是 `bus=1`，但如果你用的载板把 I2C 映射改了，需要同步改 `config/train.yaml`。

2. **ADS1115 是否真的在 `0x48`**  
   如果 `ADDR` 没有接地，地址会变。采样前建议先确认总线上能扫到设备。

3. **OPT101 输出电压是否在 ADS1115 量程内**  
   当前默认 `gain=4.096`，适合把输入控制在 0 到 4.096V 的范围内。若信号接近满量程，先看是否需要调整量程再改算法。

4. **所有模块是否共地**  
   不共地会导致读数漂移、跳变，甚至完全读不出来。

## 现场验证建议

接好线后，先做最小化验证：

```bash
i2cdetect -y 1
```

如果接线和地址正确，扫描结果里应该能看到 `0x48`。

随后再切到项目配置中的硬件模式：

```yaml
hardware:
  mode: hardware
```

如果要先排查采集链路，也可以继续使用：

```yaml
hardware:
  mode: mock
```

这样可以先验证流程与数据落盘，再接入真实硬件。

## 与代码的对应关系

| 文件 | 作用 |
|---|---|
| `ads1115.py` | ADS1115 读数、地址、量程、通道配置 |
| `opt101.py` | OPT101 采样接口统一封装 |
| `mock_sensor.py` | 无硬件时的模拟采样 |
| `sampler.py` | 根据 `mock` / `hardware` 选择采样对象并组织记录 |

## 备注

如果后续硬件改成别的 ADC，或者 OPT101 不是接在 A0，而是接到别的单端输入通道，这个目录下的说明和 `config/train.yaml` 里的 `hardware` 配置要一起同步更新。
