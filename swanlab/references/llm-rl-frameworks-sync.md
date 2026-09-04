# LLM 微调 / RL 训练框架 → SwanLab 接入（LLaMA-Factory / veRL / Swift）

> 这些框架通常由外部启动器驱动训练，接入点大多在**配置**或**启动命令**里，不在训练代码里打点。

## LLaMA-Factory

在训练配置 yaml（如 `examples/train_lora/xxx.yaml`）里加：

```yaml
### swanlab
use_swanlab: true
swanlab_project: llamafactory
swanlab_run_name: Qwen2-VL-7B-Instruct
```

然后正常启动：

```bash
llamafactory-cli train examples/train_lora/qwen2vl_lora_sft.yaml
```

启动后命令行会给出 SwanLab 实验链接。支持的参数：`use_swanlab`、`swanlab_project`、`swanlab_run_name`，以及其它与 `swanlab.init` 一致的字段。
也可以用 LLaMA Board（Web 界面）开启训练，同样能看到 SwanLab 记录。

## veRL（RL 训练，如 PPO / GRPO）

在 verL 启动命令里加 `trainer.logger=['swanlab']`（或与 console 并存）：

```bash
PYTHONUNBUFFERED=1 python3 -m verl.trainer.main_ppo \
  data.train_files=$HOME/data/gsm8k/train.parquet \
  data.val_files=$HOME/data/gsm8k/test.parquet \
  trainer.logger=['console','swanlab'] \
  ...
```

每轮评估时想记录生成文本，同理把 `trainer.logger` 设为含 `swanlab` 并在配置里开启评估日志即可。
断点续训：verl 自身支持 checkpoint 续跑，配合 SwanLab 的 `resume`/`id` 可让曲线接上。

## 其它 LLM / RL 框架（官方「集成」章节）

- **Swift**、**Unsloth**、**XTuner**、**DiffSynth**、**MLX-LM**、**torchtune**、**Sentence-Transformers**：各有对应集成入口，多在训练入口/回调处开启 swanlab。
- **BitNet / RL**：**EasyR1 / AReaL / ROLL / RLINF / MindSpeed-RL / NVIDIA-NeMo RL / RLHF (TRL)** 同理，按官方集成页在启动配置里启用 swanlab logger。

## 通用提醒

- 这些框架的指标名、step 语义与 `swanlab.log` 不同，但 SwanLab 会自动归一化到统一看板；想按 epoch 画 X 轴，可在框架侧同步一个 `epoch` 指标后用 `swanlab.define_metric(..., x_axis="...")`。
- 离线/集群环境：这些框架一般默认 online 上传；若内网跑不了，先落到本地 `swanlog/` 再补传（见 SKILL.md 的 offline 路径）。
