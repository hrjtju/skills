---
name: uv-python
description: 使用 uv（极快的 Python 包与项目管理器）管理 Python 项目环境、依赖、Python 版本与虚拟环境。当需要初始化项目、切换 Python 版本、添加/移除依赖、同步环境、配置自定义包索引（如 PyTorch CUDA wheel）、运行脚本或排查 uv 相关问题时使用。
---

# uv Python 项目管理

`uv` 是一个极快的 Python 包与项目管理器，替代 pip/venv/poetry。可用 `uv --help` 或 `uv help <command>` 获取帮助。

## 常用命令速查

| 目的 | 命令 |
|------|------|
| 新建项目 | `uv init` |
| 添加依赖 | `uv add <pkg>` |
| 移除依赖 | `uv remove <pkg>` |
| 同步环境（按 pyproject/lock 安装） | `uv sync` |
| 更新 lockfile | `uv lock` |
| 运行命令/脚本（自动使用项目环境） | `uv run <cmd>` |
| 依赖树 | `uv tree` |
| 管理 Python 版本 | `uv python <install\|list\|pin>` |
| 创建虚拟环境 | `uv venv` |
| pip 兼容接口 | `uv pip <...>` |

## Python 版本管理

- 安装指定版本：`uv python install 3.11`
- 列出可用/已装版本：`uv python list`
- 为项目固定版本（写入 `.python-version`）：`uv python pin 3.11`
- 用指定 Python 同步：`uv sync -p 3.11` 或 `uv sync --python 3.11`
- 切换项目 Python 版本的可靠流程：先 `uv python pin 3.11`（并把 `pyproject.toml` 的 `requires-python` 调整到兼容范围），删除旧 `.venv`，再 `uv sync`。

## 依赖与自定义索引（重点）

- 添加依赖：`uv add torch`
- 从特定索引安装（例如 PyTorch CUDA wheel），推荐在 `pyproject.toml` 中配置命名 index + `tool.uv.sources`，避免解析错乱：

```toml
[project]
dependencies = ["torch", "torchvision"]

[[tool.uv.index]]
name = "pytorch-cu132"
url = "https://download.pytorch.org/whl/cu132"
explicit = true          # 仅当被 sources 显式引用时才使用该 index

[tool.uv.sources]
torch = { index = "pytorch-cu132" }
torchvision = { index = "pytorch-cu132" }
```

### PyTorch CUDA wheel 版本选择

- PyTorch 官方索引地址格式为 `https://download.pytorch.org/whl/cu<版本>`，例如 CPU 用 `cpu`，CUDA 12.8 用 `cu128`，CUDA 13.2 用 `cu132`。
- 新架构显卡（如 RTX 50 系 Blackwell，sm_120）需要较新的 CUDA wheel。**本机约定使用 CUDA 13.2 的 torch，即 `cu132` 索引。**
- 可用索引列表见 <https://download.pytorch.org/whl/> ；若某个 `cuXXX` 目录不存在会解析失败，优先选官方已发布的版本。

- `explicit = true` 表示该 index 只服务于 `tool.uv.sources` 中显式指向它的包，其余包仍走默认 PyPI。
- 命令行临时指定：`uv add torch --index pytorch-cu132=https://download.pytorch.org/whl/cu132`
- 多 index 解析策略：`--index-strategy unsafe-best-match`（跨 index 找最佳版本，谨慎使用）。

## 运行与验证

- 运行脚本：`uv run python main.py`（首次会自动创建 `.venv` 并同步）
- 运行一次性检查：`uv run python -c "import torch; print(torch.cuda.is_available())"`
- `uv run` 会确保环境与 lockfile 一致后再执行。

## 常见坑（Windows / PowerShell）

- uv 的进度/信息输出走 stderr，在 PowerShell 里 `2>&1` 合并时会被包装成 `NativeCommandError`（红字）但**不代表失败**，看退出码与实际结果。
- 大型 wheel（如 torch cuXXX 数 GB）下载慢，给足超时时间。
- 切换 Python 版本后若行为异常，删掉 `.venv` 重新 `uv sync` 最稳妥。
- `requires-python` 必须覆盖目标解释器版本，否则 `uv sync -p` 会报不兼容。
