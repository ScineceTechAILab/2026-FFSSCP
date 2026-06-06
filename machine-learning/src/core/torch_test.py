import torch

print("1. PyTorch 版本:", torch.__version__)
print("2. CUDA 是否可用:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("3. 当前显卡名称:", torch.cuda.get_device_name(0))
    # 做一个简单的 GPU 矩阵计算测试
    x = torch.randn(3, 3).cuda()
    y = torch.randn(3, 3).cuda()
    print("4. GPU 计算测试成功，结果:\n", x @ y)
else:
    print("3. ❌ 警告: 无法使用 GPU 加速，只能用 CPU 计算。")