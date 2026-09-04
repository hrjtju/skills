# PyTorch Lightning → SwanLab 集成模板（默认 #2）

> 可改写模板。你的 `LightningModule` / `DataModule` / 模型请用自己的；这里演示把 Lightning 训练进度送进 SwanLab。

## 设计思路

用 SwanLab 官方提供的 `SwanLabLogger` 作为 Lightning 的 `Trainer` logger。Lightning 里所有 `self.log(...)` / `self.log_dict(...)` 的指标都会被自动记录，**不需要手写 `swanlab.log`**。

## 最小接入

```python
import pytorch_lightning as pl
from swanlab.integration.pytorch_lightning import SwanLabLogger

swanlab_logger = SwanLabLogger(
    project="my-project",          # 参数与 swanlab.init 一致
    experiment_name="resnet-baseline",
)

trainer = pl.Trainer(
    max_epochs=30,
    logger=swanlab_logger,         # ← 关键
)

trainer.fit(model, train_loader, val_loader)
```

在 `LightningModule` 里正常记指标即可：

```python
def training_step(self, batch, batch_idx):
    ...
    self.log("train_loss", loss)          # 自动进 SwanLab
    self.log_dict({"train/lr": lr, "train/acc": acc})
```

## 多次 `trainer.fit`（N 折交叉验证等）

每折结束要显式 finish，否则下一次 fit 会接着同一实验：

```python
for fold in range(N):
    logger = SwanLabLogger(project="p", experiment_name=f"..._fold{fold}")
    trainer = pl.Trainer(logger=logger)
    trainer.fit(model, train_loader, val_loader)
    logger.experiment.finish()   # ← 每次 fit 后 finish
```

## 想控制实验名/断点续训

`SwanLabLogger` 的初始化参数与 `swanlab.init` 一致，可传 `experiment_name`、`config`、`tags`、`id`/`resume`、`mode` 等。

## 与 `swanlab.init` 共用

也可以先在外部 `swanlab.init(...)` 建好实验，再把 Logger 挂到 Trainer，指标会记到外部已建的项目里（适合先定好 config 再训练）。

## 发布时

```bash
# 凭证已由环境变量 SWANLAB_API_KEY 提供（无需写死）
```
