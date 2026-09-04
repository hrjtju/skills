---
name: swanlab
description: |
  把 AI 训练进度实时同步/可视化到 SwanLab 云端（类 Weights & Biases）：安装登录、给 PyTorch / Lightning / Transformers / LLaMA-Factory 训练脚本打点记录指标（init/log/finish）、离线训练完再补传（swanlab sync）、断点续训（resume）、分布式并行共享（parallel），并用在线看板查看进度（默认示例为 PyTorch 手写循环与 Lightning）。当用户要"同步训练进度""记录训练指标""跟踪实验""训练可视化"，或提到 SwanLab、swanlab、wandb 替代、实验跟踪、断点续训时使用。路由：训练过程跟踪与实验记录 → 本 skill；数据分析/论文配图 → nature-figure / scipilot；非训练记录类写作 → nature-writing。
version: 1.0.0
license: MIT
metadata:
  author: Ivy
  tags: [training, experiment-tracking, swanlab, mlops, visualization, pytorch, resume]
  related_skills: [nature-experiment-log, nature-figure, paper-read]
---

# SwanLab — 同步 AI 训练进度

SwanLab 是一款开源 AI 训练分析平台（对标 Weights & Biases / TensorBoard）。它把训练过程里的**指标、超参数、日志、硬件占用**实时同步到云端看板，你可以在任何设备打开网页看训练曲线、对比多个实验、断点续训、多人协作。

本 skill 的核心能力是**让训练进度进入 SwanLab**：安装 → 登录 → 在你自己的训练脚本里打点记录 → 同步/查看。**脚本里的打点代码由你写，本 skill 给出思路、API 用法与可改写的模板片段，不替你写完整训练脚本**。

## 三种"进度"怎么选

SwanLab 的 `mode` 决定数据去哪，直接决定"同步"行为：

| mode | 数据去向 | 何时用 |
|------|----------|--------|
| `online`（默认） | 实时同步到云端看板 | 本机能联网，想边训边看曲线 |
| `offline` | 只写入本地 `swanlog/`，不联网 | 集群/内网/断续网络，训练完再补传 |
| `local` | 记录到本地，可用 `swanlab watch` 开本地看板 | 完全离线，用本地仪表盘 |
| `disabled` | 不记录也不上传 | 临时调试，不想留痕 |

"同步"对应两条路径：
- **online 边训边同步**：`init(mode="online")` + 训练循环里 `log(...)`。默认即此。
- **offline 事后补传**：`init(mode="offline")` 跑完训练 → `swanlab sync ./swanlog/run-xxx`。

## 快速开始（online，最常用）

### 1. 安装

```bash
pip install swanlab
# 国内加速
pip install swanlab -i https://mirrors.cernet.edu.cn/pypi/web/simple
```

### 2. 登录拿 API Key

API Key 在 [用户设置](https://swanlab.cn/settings) 页面。

```bash
# 交互式（粘贴后回车，粘贴内容不回显，属正常）
swanlab login
# 或命令行直接给 key（适合 Windows CMD / 自动化）
swanlab login -k <你的-api-key>
# 换账号：--relogin；登录私有化服务：--host <host>
```

Python 里也能登录（写入本地凭证）：

```python
import swanlab
swanlab.login(api_key="你的-api-key", save=True)
```

> 自动化为避免交互，推荐用环境变量 `SWANLAB_API_KEY`（见文末"自动化"）。

### 3. 第一个带同步的实验

拿到 `run = swanlab.init(...)` 后，用 `run.log(...)` 或全局 `swanlab.log(...)` 记录指标，脚本结束时 SwanLab 会自动 `finish`。

```python
import swanlab

run = swanlab.init(
    project="my-project",               # 项目名，默认取运行目录名
    experiment_name="resnet-baseline",  # 实验名，默认 swan-1 这类
    config={"learning_rate": 0.01, "epochs": 10},  # 超参数/元数据
)

for epoch in range(run.config.epochs):
    # ...你自己的训练/评估代码，算出 acc / loss ...
    swanlab.log({"accuracy": acc, "loss": loss})
```

运行后打开 [swanlab.cn](https://swanlab.cn)，在项目下就能看到实时曲线。

## 给训练脚本打点：核心 API

### `swanlab.init(...)`（创建/恢复实验）

常用参数：

| 参数 | 作用 |
|------|------|
| `project` / `workspace` | 项目名；`workspace` 填组织用户名时可上传到组织 |
| `experiment_name` / `description` | 实验名 / 描述 |
| `config` | 超参数字典，或 yaml/json 路径 |
| `tags` / `group` / `job_type` | 标签 / 分组 / 任务类型 |
| `mode` | `online`/`offline`/`local`/`disabled` |
| `id` + `resume` | 断点续训（见下） |
| `parallel="shared"` | 多进程分布式共享同一实验 |
| `color` | 看板区分色（名称 / `#528d59` / `rgb(...)`） |
| `logdir` | 日志保存路径，默认 `swanlog` |
| `public` | 直接建项目是否公开，默认私有 |

### `swanlab.log(data, step=None, print_to_console=False)`

`data` 为 `{指标名: 值}`，值是标量或 BaseType（图像/音频/文本）。不传 `step` 则从 0 起每次 +1。`print_to_console=True` 会把字典打到终端。

```python
swanlab.log({"train/loss": loss, "val/acc": acc})          # 标量，名字里带 / 自动分组成 train/val
swanlab.log({"img": swanlab.Image(image_tensor)}, step=e)  # 记录图片等媒体
```

### `swanlab.define_metric(...)`（摆布图表，需 ≥0.10.0）

在第一次 `log` 前调用，定制 X 轴、分组、隐藏：

```python
swanlab.define_metric("train/loss", x_axis="train/epoch")  # 用 epoch 当 X 轴（不是 step），会自动向 Y 补值
swanlab.define_metric("val/*", section_name="Validation")  # glob 批量分组
swanlab.define_metric("debug/*", hidden=True)              # 折叠到 HIDDEN 分组
```

> X 轴与 Y 轴分开两个 `log` 时，建议**先 log X（如 epoch）再 log Y**；同一项目同指标只对应一张图，跨 run 后定义不覆盖。

### `swanlab.finish()`

脚本正常结束会自动 finish。在**子进程 / Jupyter Notebook** 里跑 `init` 时，必须在结束处显式 `swanlab.finish()`。

## 断点续训（resume）

训练中断后继续，或用 checkpoint 续跑，还想要曲线接在同一个实验上：

```python
run = swanlab.init(project="p", id="14pk4qbyav4toobziszli", resume=True)
```

`resume` 取值：`True`/`"allow"`（存在则续，否则新建）、`"must"`（必须存在、必须传 id）、`"never"`（总新建）。实验 id 在实验的「环境」页或链接里，为 21 位字符串。注意**项目克隆出来的实验不能 resume**。

## 分布式 / 多进程（parallel）

多进程同时向同一实验传指标：

```python
swanlab.init(parallel="shared", id="my-distributed-run")  # 各进程 key 相同，数据汇聚；自动强制 online + resume=allow
```

## 查看进度

- **云端**：打开 [swanlab.cn](https://swanlab.cn) 项目页，看折线、媒体、日志、硬件监控。
- **本地（local/offline 数据）**：`swanlab watch` 在本地开离线看板。

## 框架集成（默认：PyTorch 手写循环 + Lightning）

本 skill 以 **PyTorch 手写循环** 与 **PyTorch Lightning** 为默认示例（见 `references/` 两个模板），其余框架列出最简接入点。接入只为把训练进度送进 SwanLab，**训练/数据代码仍由你写**。

### PyTorch（手写训练循环）— 默认 #1

最通用：`swanlab.init(project=..., config={...})` → 循环里 `swanlab.log({...})` → 结束 `finish()`。详见 `references/pytorch-training-sync.md`。

### PyTorch Lightning — 默认 #2

```python
from swanlab.integration.pytorch_lightning import SwanLabLogger

swanlab_logger = SwanLabLogger(project="my-project")   # 参数与 swanlab.init 一致

trainer = pl.Trainer(logger=swanlab_logger)
trainer.fit(model, train_loader, val_loader)
```

Lightning 里 `self.log("train_loss", loss)` 会自动记进实验。多次 `trainer.fit`（如 N 折）时，每次 fit 后加 `swanlab_logger.experiment.finish()`。详见 `references/pytorch-lightning-sync.md`。

### HuggingFace Transformers

- `transformers >= 4.50.0`：`TrainingArguments(..., report_to="swanlab")` 一行接入；项目/工作空间可设 `SWANLAB_PROJECT` / `SWANLAB_WORKSPACE` 环境变量。
- `transformers < 4.50.0`：`from swanlab.integration.transformers import SwanLabCallback` → `Trainer(..., callbacks=[SwanLabCallback(project=...)])`。

详见 `references/transformers-hf-sync.md`。

### LLaMA-Factory（LLM 微调）

训练 yaml 里加：

```yaml
use_swanlab: true
swanlab_project: your_project
swanlab_run_name: your_run
```

### veRL（RL 训练）

启动命令加 `trainer.logger=['console','swanlab']`。

### Ultralytics（YOLO）

```python
from ultralytics import YOLO
from swanlab.integration.ultralytics import add_swanlab_callback

model = YOLO("yolov8n.yaml")
add_swanlab_callback(model, project="...")   # 可在回调里自定义项目/实验名
model.train(data="./coco128.yaml", epochs=3, imgsz=320)
```

### Stable-Baselines3（强化学习）

```python
from swanlab.integration.sb3 import SwanLabCallback

model.learn(total_timesteps=..., callback=SwanLabCallback())
```

### 其它框架（官方「集成」章节逐一接入）

Swift / Unsloth / XTuner / MindSpeed-RL / PaddleDetection / PaddleYOLO / MMDetection / MMSegmentation / fastai / XGBoost / LightGBM / CatBoost / Keras / Hydra / **TensorBoard / W&B / MLflow**。已用 W&B / TensorBoard / MLflow 记录的旧事件可用 `swanlab convert` 导入。

> **已有训练代码但没打点？** 选一条路径：手写循环就手动插 `init`/`log`；已有 Logger 的回调类（Lightning/TF/SB3/Ultralytics）就直接挂对应 SwanLab 回调，改动最小。

## CLI 参考

```bash
swanlab login [-r|--relogin] [-k|--api-key <key>] [-h|--host <host>] [-w|--web-host <web>] [--local]
swanlab logout [--local]
swanlab sync [options] [logdir]     # 把本地 swanlog 上传到云端
swanlab watch                       # 打开本地离线看板
```

`swanlab sync` 常用选项：`-k/--api-key`、`-h/--host`、`-w/--workspace`、`-p/--project`、`-i/--id`（单目录时指定实验 id 做 resume 式合并）。默认同步到日志里记录的 `project`。例：

```bash
swanlab sync ./swanlog/run-xxx              # 单个实验
swanlab sync ./swanlog/run-*                # 批量
swanlab sync ./swanlog/run-xxx --id <实验ID>  # 不想新建实验，往原实验上补差异
```

## 环境变量（自动化 / 免交互）

| 变量 | 作用 |
|------|------|
| `SWANLAB_API_KEY` | 云端 API Key。登录时**优先**读它（高于本地存储），最利于 CI/无交互 |
| `SWANLAB_MODE` | `local`/`online`/`offline`/`disabled`（大小写敏感） |
| `SWANLAB_LOGDIR` / `SWANLAB_ROOT` | 日志目录 / 全局配置目录 |
| `SWANLAB_PROJ_NAME` / `SWANLAB_EXP_NAME` / `SWANLAB_WORKSPACE` / `SWANLAB_TAGS` | 等价于 `init` 对应参数，`SWANLAB_TAGS="a,b,c"` |
| `SWANLAB_API_HOST` / `SWANLAB_WEB_HOST` | 私有化部署地址 |

## 自动化 / CI 建议

1. 登录凭证由 `SWANLAB_API_KEY` 环境变量提供，**不写死在脚本里、不进 git**。本机 key 已存入**用户级环境变量**（Windows `[Environment]::SetEnvironmentVariable`，User 作用域）与 WSL `~/.bashrc`（`export SWANLAB_API_KEY=...`），登录时自动读取，无需交互。
2. 若是**多人共用机器**：`swanlab login --local` 只把凭证存到当前目录 `.swanlab/`；或用 `SWANLAB_API_KEY` 环境变量覆盖，不落盘。
2. 训练脚本用 `mode=os.environ.get("SWANLAB_MODE", "online")` 便于切换上线/离线。
3. 需要多账号隔离/多人共用机器时：`swanlab login --local` 只把凭证存到当前目录 `.swanlab/`（会自动生成 `.gitignore`）。

## 常见坑

- **Windows CMD 粘贴不出 key**：用 `swanlab login -k <key>` 或在 Python 里 `swanlab.login(...)`。
- **子进程/Notebook 里曲线没结束/没同步**：记得显式 `finish()`；subprocess 需在子进程末尾 finish。
- **按 epoch 而不是 step 画图**：`define_metric(..., x_axis="train/epoch")`，且先 log X 再 log Y。
- **集群跑完想补传**：训练时 `mode="offline"`，完事 `swanlab sync ./swanlog/run-xxx`。
- **共用服务器 key 冲突**：`--local` 项目级登录，互不覆盖。
- **`define_metric` 不生效**：指标已被 `log` 过后定义无效，需在首次 `log` 前定义；多媒体忽略 `x_axis`。
- **`resume` 报错**：确认 id 存在、不是克隆实验、`must` 模式下 id 必传。

## 相关文件

| 文件 | 用途 |
|------|------|
| `references/pytorch-training-sync.md` | **默认 #1** PyTorch 手写循环打点模板（含 resume / define_metric / offline） |
| `references/pytorch-lightning-sync.md` | **默认 #2** PyTorch Lightning 集成（SwanLabLogger + Trainer） |
| `references/transformers-hf-sync.md` | HuggingFace Transformers（report_to 与 SwanLabCallback 两路） |
| `references/llm-rl-frameworks-sync.md` | LLaMA-Factory / veRL / Swift 等 LLM 与 RL 训练接入 |
| `references/cv-sb3-sync.md` | Ultralytics / Stable-Baselines3 接入 |
