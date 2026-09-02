---
name: workflow-feedback
description: 在对话中捕获用户对 agent 行为的显式纠正与可复用偏好，静默追加条目到当前仓库的 docs/agent-feedback/，供 workflow-improver 使用。触发场景：用户纠正训练方式/超参数/绘图/代码合规与诚信/Windows 命令/任务流程，或给出可复用偏好。
---

# Workflow Feedback（反馈捕获）

目标：把对话里的纠正"编译"进文件，让 improver 有素材可依；捕获零摩擦，不打断对话。

## 触发条件

用户显式纠正或给出可复用偏好。按六类识别：

| 类 | 典型信号 |
|---|---|
| TRAIN | 训练方式、模型结构、数值方法（"保持 GPU 版本"、"用归一化 Hermitte 基"） |
| HYPER | 超参数、网格、分辨率（"dt 调小"、"谱截断到 16"、"不要缩水分辨率"） |
| PLOT | 绘图样式（"不同不动点用不同 marker"、"figsize 缩小"、"ticklabel 放大"） |
| INTEGRITY | 代码合规、学术诚信（"与论文形式等价"、"先检查变换前后"、"无效 run 标记"） |
| CMD | Windows 命令/环境错误（PowerShell 报错、编码、git 授权） |
| PROCESS | 任务流程（"开始前先告诉我计划"、"先出图"、"完成后 sync"） |

## 不记录（排除规则）

- 模糊抱怨、纯问答；
- 数字/实验结果类反馈 → 写 docs/worklog.md，不进 feedback 库；
- 已编码在 AGENTS.md/CLAUDE.md 的规则（避免重复沉淀）；
- 用户明确说"这条不算" → 已有条目标记 dismissed。

## 动作

1. 确定仓库：cwd 的 git 根；仅当该仓库存在 docs/agent-feedback/ 目录时才记录（试点仓库已启用）。
2. 追加条目到 docs/agent-feedback/YYYY-MM-DD.md（当天文件不存在则创建）。
3. 条目 id：YYYY-MM-DD-<CATEGORY>-<当天该类两位序号>，例如 2026-08-25-PLOT-01。
4. 同一场景重复纠正：已存在 open 条目则 count+1，不新建。
5. 任务结束用一句话汇报："记录了 N 条反馈（类别分布）"；未记录则不必提。

## 条目模板

```markdown
---
date: YYYY-MM-DD
repo: <仓库名>
category: <TRAIN|HYPER|PLOT|INTEGRITY|CMD|PROCESS>
source: user
agent: codex
session: <可选，rollout 文件名>
status: open
count: 1
---

## 场景
<一句话：什么任务/什么环节>

## Agent 实际做了什么
<agent 做了什么，或缺失>

## 期望
<用户期望的行为>

## 理由
<用户给出的理由/原话要点>
```

## 状态图例

- open：待 improver 处理
- applied：已合入 base skill
- rejected：用户拒绝（附理由）
- dismissed：不成立/不算
- needs-confirm：improver 拿不准，待确认

## 质量纪律

- 忠实记录用户原话要点，不臆造理由；
- 条目自包含：improver 不需要看原对话就能理解；
- 只记录，不改 base skill 与代码。
