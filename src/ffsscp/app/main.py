from pathlib import Path

from ffsscp.app.config_loader import load_configs
from ffsscp.app.flows import run_collect, run_predict_from_csv, run_predict_from_live, run_train


def prompt_float(message: str) -> float:
    while True:
        try:
            return float(input(message).strip())
        except ValueError:
            print("输入无效，请输入数字。")


def prompt_text(message: str) -> str:
    while True:
        value = input(message).strip()
        if value:
            return value
        print("输入不能为空。")


def main(config_path: str = "config/train.yaml") -> None:
    hardware_config, collect_config, train_config, predict_config = load_configs(config_path)

    while True:
        print("\nFFSSCP 主菜单")
        print("1. 数据采集")
        print("2. 模型训练")
        print("3. 模型预测")
        print("0. 退出")
        choice = input("请选择功能: ").strip()

        if choice == "1":
            concentration = prompt_float("请输入悬浮物浓度: ")
            csv_path, txt_path = run_collect(hardware_config, collect_config, concentration)
            print("采集完成: {}".format(csv_path))
            print("标签完成: {}".format(txt_path))
        elif choice == "2":
            _, history = run_train(train_config)
            print(
                "训练完成: train_loss={:.6f} val_loss={:.6f}".format(
                    history["train_loss"][-1], history["val_loss"][-1]
                )
            )
            print("模型目录: {}".format(Path(train_config.output_dir)))
        elif choice == "3":
            print("1. 导入 CSV 预测")
            print("2. 现场采样预测")
            predict_mode = input("请选择预测模式: ").strip()
            if predict_mode == "1":
                csv_path = prompt_text("请输入 CSV 文件路径: ")
                prediction = run_predict_from_csv(csv_path, predict_config, train_config.device)
                print("预测浓度: {:.6f}".format(prediction))
            elif predict_mode == "2":
                csv_path, prediction = run_predict_from_live(
                    hardware_config, collect_config, predict_config, train_config.device
                )
                print("采样文件: {}".format(csv_path))
                print("预测浓度: {:.6f}".format(prediction))
            else:
                print("无效选择。")
        elif choice == "0":
            print("已退出。")
            return
        else:
            print("无效选择。")
