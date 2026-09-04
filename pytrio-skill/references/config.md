# 环境变量与进程内配置

PyTRIO 在导入时读取进程环境变量，适合 CI、容器、无法交互登录的环境。也可以在创建任何 client 前用 `pytrio.configure(...)` 在进程内覆盖配置。官方文档：`docs/advanced/configuration`。

## 环境变量

| 环境变量 | 等效 Python 配置 | 说明 |
|---|---|---|
| `PYTRIO_API_KEY` | `pytrio.configure(api_key=...)` | 当前进程使用的 API Key，可替代 `trio login` |
| `PYTRIO_BASE_URL` | `pytrio.configure(base_url=...)` | Trio 服务根地址；末尾的 `/api` 和 `/` 会被归一化 |
| `PYTRIO_ENV` | `pytrio.configure(env=...)` | 当前进程使用的本地 server profile |
| `PYTRIO_LOG_LEVEL` | `pytrio.configure(log_level=...)` | SDK 与 CLI 日志等级 |

示例（CI 用环境变量注入）：

```bash
export PYTRIO_ENV=dev
export PYTRIO_API_KEY=trio-key
export PYTRIO_BASE_URL=https://beta.pytrio.cn
export PYTRIO_LOG_LEVEL=DEBUG
python train.py
```

等效的进程内配置：

```python
import pytrio
pytrio.configure(
    env="dev",
    api_key="trio-key",
    base_url="https://beta.pytrio.cn",
    log_level="DEBUG",
)
```

## 加载顺序

配置按以下顺序加载，后加载的值覆盖先前的值：

1. SDK 默认值；
2. 磁盘中的当前 profile；
3. `PYTRIO_*` 环境变量；
4. 用户调用 `pytrio.configure(...)`；
5. `ServiceClient` 等调用点的显式参数。

`PYTRIO_ENV` 会先选择并加载对应 profile，API Key、服务地址和日志等级再覆盖该 profile。环境变量只影响当前进程，不修改 `env.toml` 或 profile 的 `config.toml`。未定义、空字符串或只含空白的变量不会覆盖已有配置。

`PYTRIO_LOG_LEVEL` 支持 `DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`；其他值会在导入时触发 `configuration.invalid_environment`。

## Client 配置快照

根 `ServiceClient` 在构造开始时复制当前进程配置。它创建的所有 Control、Actor、Telemetry、下载器、执行器和派生 Client 都使用这份运行时快照。之后调用 `pytrio.configure(...)` 只影响后续新建的根 Client。

```python
import pytrio
pytrio.configure(timeout=10)
first = pytrio.ServiceClient()
pytrio.configure(timeout=30)
second = pytrio.ServiceClient()
# first 继续用 10 秒超时；second 用 30 秒超时。
```

## 常见用法

- 想交互登录：直接 `trio login`（API Key 存入本地 profile）。CLI 命令是 `trio`，不是 `pytrio`。
- 想在 CI 注入 Key：设 `PYTRIO_API_KEY`，或 `pytrio.configure(api_key=...)`。
- 想连测试/私有服务：设 `PYTRIO_BASE_URL` 或 `base_url`；`/api` 与末尾 `/` 会被归一化。
- 想让 `ServiceClient` 用某组配置：在 `pytrio.configure` 之后再创建 `ServiceClient`，因为 Client 在构造时快照配置。
