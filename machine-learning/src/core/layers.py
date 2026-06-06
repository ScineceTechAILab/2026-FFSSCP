import torch
import torch.nn as nn

class Network(nn.Module):
    def __init__(self):
        super(Network, self).__init__()
        #两层神经网络
        self.hidden1 = nn.Linear(1, 16)     #第一隐藏层，接受1维输入，输出16维
        self.hidden2 = nn.Linear(16, 8)     #第二隐藏层，接受来自上层的输出，输出8维
        self.output = nn.Linear(8, 1)       #输出1维
        self.relu = nn.ReLU()

    def forward(self, x):
        #前向传播
        x = self.hidden1(x)
        x = self.relu(x)
        x = self.hidden2(x)
        x = self.relu(x)
        x = self.output(x)
        return x
