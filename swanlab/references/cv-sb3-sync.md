# 目标检测 / 强化学习框架 → SwanLab 接入（Ultralytics / Stable-Baselines3）

## Ultralytics（YOLO 目标检测）

用官方回调 `add_swanlab_callback`，把 `model` 传入即可：

```python
from ultralytics import YOLO
from swanlab.integration.ultralytics import add_swanlab_callback

model = YOLO("yolov8n.yaml")
model.load()

add_swanlab_callback(model)                 # 默认项目名
# 自定义：
# add_swanlab_callback(model, project="det", experiment_name="yolov8n-coco128")

model.train(data="./coco128.yaml", epochs=3, imgsz=320)
```

多卡 / DDP 训练：用 `return_swanlab_callback`（按官方集成页），以便在多进程下只让主卡上报、避免重复实验。

## Stable-Baselines3（强化学习）

用 `SwanLabCallback` 作为 `model.learn` 的 callback：

```python
from stable_baselines3 import PPO
from swanlab.integration.sb3 import SwanLabCallback

model = PPO("MlpPolicy", env)
model.learn(
    total_timesteps=200_000,
    callback=SwanLabCallback(project="sb3-ppo"),   # 参数同 swanlab.init
)
```

## 其它 CV 框架（官方「集成」章节）

- **MMDetection / MMSegmentation / MMEngine / MMPretrain**：在配置/引擎处启用 swanlab（多经 `swanlab` 回调或 logger）。
- **PaddleDetection / PaddleYOLO / PaddleNLP**：有对应集成入口。
- **fastai / Keras / XGBoost / LightGBM / CatBoost**：Swankit 层或半自动回调，按官方集成页接入。

## 通用提醒

- 想要按 epoch / timestep 画 X 轴，可用 `swanlab.define_metric(..., x_axis="...")`（需 ≥0.10.0）。
- DDP / 多卡训练默认会多进程上报；用框架侧的 `return_*` 回调或 `parallel="shared"` 汇聚到同一实验，避免重复。
