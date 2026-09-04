# OpenAI 兼容 API

训练好的 LoRA 权重或基础模型可以通过 OpenAI 兼容端点接入应用。官方文档：`docs/advanced/openai`。

## 端点与鉴权

- base URL：`https://pytrio.com/api/openai/v1`
- model：权重路径（在 WebUI「权重」选项卡里复制，通常是 `save_weights_for_sampler` 返回的 `path`），或基础模型名
- api_key：你的 PyTRIO API Key（「总览」选项卡复制）

```python
from openai import OpenAI

BASE_URL = "https://pytrio.com/api/openai/v1"
MODEL_PATH = "YOUR_MODEL_PATH"  # 权重路径或基模名称
api_key = "YOUR_TRIO_API_KEY"

client = OpenAI(base_url=BASE_URL, api_key=api_key)
```

## 对话 / 流式对话 / 文本续写

`model` 必须是上面说的权重路径或基模名，不能填占位符。

```python
response = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{"role": "user", "content": "what's your name?"}],
    max_tokens=50, temperature=0.7, top_p=0.9,
)
print(response.choices[0].message.content)
```

流式：

```python
stream = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{"role": "user", "content": "你好，请简单介绍一下你自己。"}],
    max_tokens=1024, temperature=0.7, top_p=0.9, stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    if content := chunk.choices[0].delta.content:
        print(content, end="", flush=True)
```

文本续写：

```python
response = client.completions.create(
    model=MODEL_PATH, prompt="what's your name?",
    max_tokens=50, temperature=0.7, top_p=0.9,
)
print(response.choices[0].text)
```

## 图像对话

PyTRIO 只接受 **Base64 Data URL**，不能直接传本地路径或普通图片 URL。图片用 JPEG 时 MIME 为 `image/jpeg`，PNG 时改为 `image/png`。模型必须是支持图像输入的多模态模型。

```python
import base64
from pathlib import Path
from openai import OpenAI

BASE_URL = "https://pytrio.com/api/openai/v1"
MODEL_PATH = "YOUR_MODEL_PATH"
IMAGE_PATH = Path("YOUR_IMAGE_PATH")
IMAGE_MIME_TYPE = "image/jpeg"

image_base64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")
image_data_url = f"data:{IMAGE_MIME_TYPE};base64,{image_base64}"

client = OpenAI(base_url=BASE_URL, api_key="YOUR_TRIO_API_KEY")
stream = client.chat.completions.create(
    model=MODEL_PATH,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "请描述这张图片。"},
            {"type": "image_url", "image_url": {"url": image_data_url}},
        ],
    }],
    max_tokens=1024, temperature=0.7, top_p=0.9, stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    if content := chunk.choices[0].delta.content:
        print(content, end="", flush=True)
```

## 要点

- 先把权重保存好（`save_weights_for_sampler`），再拿返回的 `path` 当 `model`。基础模型直接用 `client.get_supported_models()` 里的名字。
- 图像对话只能走 Base64 Data URL，且 MIME 要和真实编码一致。
- 这不是 `pytrio` SDK 的调用方式；OpenAI 兼容端点面向已训练模型的部署与应用接入。
