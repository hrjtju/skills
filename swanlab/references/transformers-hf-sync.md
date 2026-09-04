# HuggingFace Transformers → SwanLab 集成模板

> 可改写模板。你的模型 / tokenizer / dataset 请用自己的；这里演示把 Transformers 训练进度送进 SwanLab。分两种：新版一行 `report_to`，旧版用 `SwanLabCallback`。

## 版本判断

- `transformers >= 4.50.0`：官方已内置 SwanLab，用 `report_to="swanlab"`。
- `transformers < 4.50.0`：用 `swanlab.integration.transformers.SwanLabCallback`。

## path A：新版本（一行接入）

```python
from transformers import TrainingArguments, Trainer

args = TrainingArguments(
    output_dir="./out",
    report_to="swanlab",        # ← 关键
    run_name="great_try_1",     # 实验名（默认取 output_dir）
)

trainer = Trainer(..., args=args)
trainer.train()
```

自定义项目/工作空间（用环境变量，别写死进代码）：

```bash
export SWANLAB_PROJECT="qwen2-sft"
export SWANLAB_WORKSPACE="EmotionMachine"
```

## path B：旧版本（SwanLabCallback）

```python
from transformers import Trainer, TrainingArguments
from swanlab.integration.transformers import SwanLabCallback

swanlab_callback = SwanLabCallback(project="hf-visualization", experiment_name="TransformersTest")

trainer = Trainer(
    ...,
    callbacks=[swanlab_callback],   # ← 关键
)
trainer.train()
```

## 扩展：每个 epoch 结束后记录推理文本

继承 `SwanLabCallback` 覆盖生命周期函数，在 `on_epoch_end` 里用 `swanlab.log`：

```python
from swanlab.integration.transformers import SwanLabCallback
import swanlab

class NLPSwanLabCallback(SwanLabCallback):
    def on_epoch_end(self, args, state, control, **kwargs):
        super().on_epoch_end(args, state, control, **kwargs)
        # ... 用你的模型推理几个样例 ...
        swanlab.log({"Prediction": test_text_list}, step=state.global_step)
```

## 说明

- 指标名默认按 `argparse` 层级命名（如 `train/xxx`、`eval/xxx`），可在看板里分组。
- 想要更细粒度自定义（按 epoch 画 x 轴、隐藏某些图），可在其他框架场景里用 `swanlab.define_metric`；HF 场景通常默认 step 轴即可。
