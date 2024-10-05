import utils
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import torch
from torchinfo import summary

import torch.nn as nn


def save(folder_name, log: utils.Logger, model, device,  hyperparams={}):
    # 保存先フォルダを作成
    root = './result/' + \
        str(datetime.datetime.now().strftime(
            '%Y-%m-%d_%H-%M_')) + folder_name + '/'
    os.makedirs(root, exist_ok=True)

    # ハイパーパラメータを保存
    with open(root+'hyperparameters.txt', mode='w') as f:
        for key, value in hyperparams.items():
            f.write(f'{key}: {value}\n')

    # ログを保存
    df = pd.DataFrame(log.log)
    df.to_csv(root+'log.csv', index=False)

    # モデル構造を保存
    with open(root+'summary.txt', mode='w') as f:
        f.write(repr(summary(model, (64, 3, 32, 32), device=device, verbose=0)))

    # 損失のグラフを保存
    plt.plot(log.log['epoch'], log.log['train_loss'], label='train_loss')
    plt.plot(log.log['epoch'], log.log['test_loss'], label='test_loss')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig(root+'loss.png')
    plt.close()

    # 精度のグラフを保存
    plt.plot(log.log['epoch'], log.log['train_accuracy'],
             label='train_accuracy')
    plt.plot(log.log['epoch'], log.log['test_accuracy'], label='test_accuracy')
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.legend()
    plt.savefig(root+'accuracy.png')
    plt.close()
