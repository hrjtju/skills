# RestClient：下载权重、列 checkpoint / 训练运行

用 `ServiceClient.create_rest_client()` 拿一个 `RestClient`，负责 REST 操作（列权重、取下载链接、查训练运行、删 checkpoint 等）。官方文档：`docs/api/RestClient`、`docs/guide/download`。

## 下载训练后的 LoRA 权重

下载流程三步：取权重 ID → 拿临时下载 URL → 下载到本地。

```python
import requests
import pytrio as trio

service_client = trio.ServiceClient()
rest_client = service_client.create_rest_client()

# 1) 拿到权重 ID（也可在 WebUI「权重」页复制）
checkpoints = rest_client.list_user_checkpoints().result()
# checkpoints 里的 checkpoint_id 字段就是要用的 ID

# 2) 取临时下载 URL
checkpoint_id = "YOUR_CHECKPOINT_ID"
response = rest_client.get_checkpoint_archive_url(checkpoint_id)
download_url = response.result().url

# 3) 下载
save_filename = f"{checkpoint_id}.zip"
with requests.get(download_url, stream=True) as result:
    result.raise_for_status()
    with open(save_filename, "wb") as file:
        for chunk in result.iter_content(chunk_size=8192):
            file.write(chunk)
```

## 列出 / 查询

```python
# 当前用户的所有模型权重（分页）
checkpoints = rest_client.list_user_checkpoints(limit=100, offset=0).result()

# 当前用户的训练运行（分页）
runs = rest_client.list_training_runs(limit=10, offset=0).result()

# 某个训练运行的详情
run = rest_client.get_training_run(training_run_id="run-001").result()

# 某个训练运行下的所有 checkpoint
ckpts = rest_client.list_checkpoints(training_run_id="run-001").result()

# 会话 / 采样器信息
sessions = rest_client.list_sessions().result()
session = rest_client.get_session(session_id="sess-abc").result()
sampler = rest_client.get_sampler(sampler_id="sampler-xyz").result()
```

## 删除 checkpoint

```python
rest_client.delete_checkpoint(
    training_run_id="run-001",
    checkpoint_id="ckpt-step100",
).result()
```

## 要点

- `RestClient` 的这些调用都返回 future，需要 `.result()`（个别返回 `ConcurrentFuture`/`APIFuture`，`await` 或 `.result()` 均可）。
- `list_user_checkpoints` / `list_training_runs` / `list_sessions` 都支持 `limit`/`offset` 分页。
- 下载的是 zip / checkpoint 存档；要部署到 OpenAI 兼容端点时，用 `save_weights_for_sampler` 返回的 `path` 当 `openai` 的 `model`，不必重复下载。
- 想直接把权重接到推理服务，参考 `references/openai.md`。
