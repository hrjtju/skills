---
name: shepherd
description: "Run and supervise sandboxed agent tasks with Shepherd — a meta-agent runtime that records every agent run as a reversible, Git-like execution trace with retained outputs, so a supervisor can inspect, fork, replay, select, apply, or discard any run without touching the workspace. Use when the user wants an agent task executed in a reviewable sandbox (work lands as a proposal, never directly in the tree), wants to inspect/audit what an agent changed, wants run history, changesets, or retained outputs, wants to keep/apply/discard a run's output, or wants to build meta-agent workflows (supervise another agent's execution). Triggers: 'shepherd', '可逆 agent 执行', 'retained output', '审阅 agent 的改动', 'meta-agent', '先让 agent 在沙箱里跑', 'fork/replay agent run'."
compatibility: "shepherd-ai 0.3.0 installed via `uv tool install shepherd-ai`. CLI: `shepherd` (or absolute ~/.local/bin/shepherd). Task scripts need the package venv python: ~/.local/share/uv/tools/shepherd-ai/bin/python. macOS Seatbelt sandbox enforced; Linux Landlock (privileged container); Windows unsupported. Agent lane needs the `claude` CLI (present at /usr/local/bin/claude)."
---

# Shepherd — 可逆执行 trace 的 meta-agent 运行时

Shepherd 把"让一个 agent 干活的运行"记录成**可逆的 Git 式 trace**：agent 的所有产物先落在
**retained outputs**（侧边提案区），不进工作区。监督者先 `run changeset` 审查，再
`select` / `apply` / `discard` 结算。签名即权限面：task 参数里 `repo: sp.GitRepo`
就是唯一写授权，OS 层（macOS Seatbelt）强制执行，越权写直接被系统调用拒绝。

> 已安装：shepherd-ai 0.3.0（`uv tool install shepherd-ai`），CLI 在
> `~/.local/bin/shepherd`。若 shell 找不到 `shepherd`，先 `export PATH="$HOME/.local/bin:$PATH"`。
>
> **本机当前选择：static 通道**（离线、零认证、零成本）——见下方两通道对比；未配置任何 Anthropic 认证。

## 工作区（Workspace）生命周期

```bash
export PATH="$HOME/.local/bin:$PATH"
mkdir -p ~/ws && cd ~/ws
shepherd init                # 把当前目录变成 Shepherd workspace（建 .vcscore）
shepherd doctor              # 检查环境就绪；--json 输出机器可读结果
```

- 每个 workspace 独立；`shepherd run *` 命令都作用于当前目录的 workspace。
- shell 状态不跨 bash 调用持久：每条命令都在 workspace 目录下执行。

## 两条运行通道

### 1) 确定性通道（无 agent、无需 API key）— 用于演示 / 测试 / 纯产物工作流

```bash
cd <workspace>
shepherd demo write quickstart > quickstart_demo.py
~/.local/share/uv/tools/shepherd-ai/bin/python quickstart_demo.py   # 必须用这个 python（含 shepherd 包）
```

### 2) Agent 通道（让 Claude 干活，产物进沙箱）— 正式使用

```bash
cd <workspace>
shepherd doctor claude          # 确认 claude CLI / 登录 / 沙箱就绪（claude setup-token 可生成长期 token）
shepherd demo write agent-task > agent_task.py
# 编辑 agent_task.py 里的 PROMPT / 签名（= 权限面），然后：
~/.local/share/uv/tools/shepherd-ai/bin/python agent_task.py
```

agent 的产出进入 retained outputs；**你的文件一个都不会被动**，直到你结算。

## Task 写法（签名 = 权限面）

```python
import shepherd as sp

@sp.task
def write_program(repo: sp.GitRepo, prompt: str, output_path: str = "program.py") -> None:
    """Write a small self-contained Python program that does what `prompt` asks.
    Save it to output_path. It must run with plain python3, read no input,
    and finish on its own within about ten seconds."""
```

- `repo: sp.GitRepo` = 显式可写授权；`May[GitRepo, ReadOnly]` = 只读
  （越权写在沙箱内被 syscall 拒绝）。
- 未标注的 `repo` 参数只是普通参数，不是授权。
- 多仓库：`May[GitRepo, ReadWrite]`，用 `ws.bind(root="backend/", name="backend")` 绑定。

## 审查与结算（每次 run 之后）

```bash
shepherd run list                        # 所有 run 与状态
shepherd run show <run-ref>              # 单次 run 详情（--latest 最近一次；--json 机器输出）
shepherd run changeset --latest          # 它到底改了什么（只读视图）
shepherd run trace --latest --events     # 完整可逆 trace
shepherd run select  <run-ref>           # 保留这次产出
shepherd run apply   <run-ref>           # 把产出 3-way merge 进工作区（路径无冲突时）
shepherd run release <run-ref>           # 释放（从 retained 转正式）
shepherd run discard <run-ref>           # 丢弃
```

## 两条通道的区别（static vs claude）

| | static（确定性通道） | claude（agent lane） |
|---|---|---|
| 调用 LLM？ | ❌ 不调用任何模型 | ✅ 在 Seatbelt 沙箱里跑 `claude -p` 真实 agent |
| 能力 | 按 task 的 kwargs 生成固定产物（写文件/走流程/测机制） | 理解自然语言任务，自主写代码、改文件、迭代 |
| 认证 | 无需任何 key，离线可用 | 需要 claude CLI 可认证（见下） |
| 可复现 | 完全可复现、免费 | 不可复现、按量计费 |
| 适合 | 演示 / 测试 / 确定性流水线 | 真正让 AI 干活 |

**不想用 Anthropic 官方服务？** claude lane 的认证三选一：
1. `ANTHROPIC_API_KEY`（Anthropic 官方 key，或任何**兼容网关**的 key）
2. `CLAUDE_CODE_OAUTH_TOKEN`（订阅）
3. `claude login`（订阅）

沙箱 jail 继承宿主全部环境变量（源码 `vcs_core/_seatbelt_containment.py` 默认 `env=dict(os.environ)`），claude CLI 原生支持 `ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`——所以可以用自建网关（one-api / new-api）或 DeepSeek / Kimi / GLM 等官方 Anthropic 兼容端点，把请求指向任意模型后端：

```bash
export ANTHROPIC_BASE_URL=https://your-gateway.example.com   # 或兼容端点
# 与 API key 二选一或同时：
export ANTHROPIC_AUTH_TOKEN=sk-...   # 网关 token
# 或 export ANTHROPIC_API_KEY=sk-...
shepherd doctor claude --probe        # 实测认证 + 沙箱链路
```

注意：`codex` 等其它 provider 在 0.3.0 里是 `deferred`（源码 `runtime_provider.py` 显式拒绝），当前版本 agent lane 只有 claude 壳，但后端模型可以任意。

## 已知行为（v0.3.0 alpha，实测）

- 结算（select/apply/release/discard）会把决策、证据、产物完整记录进 vcscore 世界存储（`~/.vcscore`），`run outputs` / `run show` 可查状态，`changeset --latest --read <path>` 可随时读回产物内容。
- **select/apply 后文件不会自动写回工作目录**——产物以树形式留在 run 的 output 中，需要通过 `changeset --read` 读取后自行落盘（或等后续版本接通物化同步）。审查和追溯不受影响。

## 常用规则

- **永远先 `changeset` 再结算**：先看它改了哪些路径、读 preview，再决定 select/apply/discard。
- `run changeset --latest --read <path>` 可直接在终端预览文件内容。
- 一个 run 只结算一次（select/apply/discard 互斥）。
- trace 保留历史：即使 discard 也有记录，可追溯。
- 跨模型/跨 harness 的 meta-agent 编排（让 agent A 审查 agent B 的 trace）：每个维度开新 run，
  读对方 run 的 `show --json` / `changeset` 作为证据，不要在同一上下文里凭印象判断。

## 停止与上报

- agent lane 需要 claude 登录或 `ANTHROPIC_API_KEY`：`shepherd doctor claude --probe` 可实测认证。
- HTTP 403 = 账号/组织限制，不是登录问题。
- 沙箱内 agent 卡死会以 budget timeout 呈现（不是认证错误）。
- 本机环境：Python 3.11+（venv 内 3.11.11）✓ · macOS ✓ · Windows 不支持。
