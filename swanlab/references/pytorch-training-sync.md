# PyTorch 手写训练循环 → SwanLab 同步模板

> 这是一个**可改写的模板**，不是替你写好的完整训练脚本。你的 `train()` / `evaluate()`、模型、数据 loader 请用你自己的；这里只演示在正确的位置插入 SwanLab 打点。三处标注 `← 你的代码` 的地方请替换。

## 设计思路

- 用 `mode` 区分上线/离线：`online` 边训边传云端；`offline` 存本地 `swanlog/`，集群跑完再用 `swanlab sync` 补传。
- 用 `config` 收纳超参数，看板里直接对比。
- `define_metric("train/*", x_axis="train/epoch")` 让曲线横轴是 epoch 而非 step。
- `resume=True, id=...` 支持从 checkpoint 续跑时曲线接在同一个实验上。

## 模板骨架

```python
import os
import swanlab

# 0. 训练开始前：从 checkpoint / 环境确定是否续训
RESUME_ID = os.environ.get("SWANLAB_RESUME_ID")      # 续跑时填上次实验 id；新实验留空
MODE = os.environ.get("SWANLAB_MODE", "online")       # online / offline 可在外部切换

# 1. 初始化实验
run = swanlab.init(
    project="my-project",                # ← 你的项目名
    experiment_name="resnet-baseline",   # ← 你的实验名
    config={
        "learning_rate": 1e-3,           # ← 你的超参数
        "batch_size": 64,
        "epochs": 30,
    },
    mode=MODE,
    resume=True if RESUME_ID else None,  # 有 id 就续，否则新建
    id=RESUME_ID,
)

# 2.（可选）定制图表：横轴用 epoch，并把 train/val 分组
swanlab.define_metric("train/*", x_axis="train/epoch", section_name="Train")
swanlab.define_metric("val/*",  x_axis="train/epoch", section_name="Validation")

# 3. 训练循环
for epoch in range(start_epoch, run.config["epochs"]):
    # --- train 阶段（你的代码）---
    # train_loss = train_one_epoch(model, loader, ...)   ← 你的代码
    swanlab.log({"train/epoch": epoch, "train/loss": train_loss})

    # --- val 阶段（你的代码）---
    # val_loss, val_acc = evaluate(model, loader, ...)    ← 你的代码
    swanlab.log({"train/epoch": epoch, "val/loss": val_loss, "val/acc": val_acc})

# 4. 结束（脚本正常结束也会自动 finish；子进程里显式调用更稳妥）
swanlab.finish()
```

## 离线跑完再补传

训练时设置 `SWANLAB_MODE=offline`（或 `mode="offline"`）→ 数据存到默认为 `swanlog/` 目录 → 在能联网的机器上：

```bash
swanlab sync ./swanlog/run-xxx            # 上传（项目取日志里记录的 project）
swanlab sync ./swanlog/run-xxx --id <实验ID> # 不想新建实验，往原实验补差异
```

## 从 checkpoint 续跑

关键：先确定上次的 `run.id`（在实验「环境」页 / URL 里），再带着 `resume=True` 和 `id` 重新 `init`。`resume=True` 等价 `"allow"`（存在则有，否则新建）；要严格续就 `resume="must"`。

> 注意：项目**克隆**出来的实验不能被 resume；`mode` 缺省 online 会在离线环境失败，因此离线场景记得显式 `mode="offline"`。

## 发布时的 git 安全

```bash
# 凭证不进仓库
echo "swanlog/" >> .gitignore
# 多人共用服务器则项目级登录（凭证存当前目录 .swanlab/，自动生成 .gitignore）
swanlab login --local
```
