# Logprobs：`sample()` 与 `compute_logprobs()`

PyTRIO 有两种获取 token 级 logprobs 的方式，回答的问题不同，别混用。官方文档：`docs/advanced/compute_logprobs`。

| 方式 | 适合场景 | 能拿到什么 |
|---|---|---|
| `sample()` | 让模型继续生成，并记录这次采样过程 | prompt token 的 logprobs、本次生成 token 的 logprobs |
| `compute_logprobs()` | 已经有一段完整文本，用指定模型重新打分 | 输入全文中每个实际 token 的 logprobs |

简言之：`sample()` 回答“模型这次采样时，每个 prompt token 和生成 token 的概率是多少”；`compute_logprobs()` 回答“给定这一整段文本，指定模型对其中每个 token 有多认可”。

## 方式一：用 `sample()` 拿 logprobs

`sample()` 默认在 `sequences[*].logprobs` 里返回生成 token 的 logprobs；设置 `include_prompt_logprobs=True` 还会返回 prompt token 的 logprobs。`topk_prompt_logprobs` 可返回 prompt 部分 top-k logprob（`0` 表示不返回）。

```python
response = sampling_client.sample(
    prompt=trio.ModelInput.from_ints(prompt_ids),
    sampling_params=trio.SamplingParams(max_tokens=8, temperature=0.7),
    include_prompt_logprobs=True,
).result()

sequence = response.sequences[0]
prompt_logprobs = response.prompt_logprobs   # list[float | None]，长度和 prompt_ids 一致
completion_logprobs = list(sequence.logprobs) # list[float | None]，长度和 sequence.tokens 一致
completion_tokens = list(sequence.tokens)
```

`SampleResponse` 关键字段：`sequences`（含 `stop_reason`/`text`/`tokens`/`logprobs`）、`prompt_logprobs`、`topk_prompt_logprobs`、`output_tokens`。

看每个 token 更直观：

```python
completion = [
    {"token_id": t, "token": tokenizer.decode([t]), "logprob": lp}
    for t, lp in zip(sequence.tokens, sequence.logprobs)
]
```

## 方式二：用 `compute_logprobs()` 拿全文 logprobs

`compute_logprobs(prompt: ModelInput) -> APIFuture[list[float | None]]` 不生成新 token，而是对传入的一整段 `ModelInput` 做前向评分。返回值和输入 token 一一对齐：第 `i` 个值是第 `i` 个 token 在**前文 token 条件**下的 log probability。第一个 token 没有前文条件，可能返回 `None`。返回的是每个实际 token 的对数概率，**不是**整个词表的概率分布。

```python
text = tokenizer.apply_chat_template(messages, tokenize=False)
tokens = tokenizer.encode(text, add_special_tokens=False)
logprobs = sampling_client.compute_logprobs(
    prompt=trio.ModelInput.from_ints(tokens),
).result()  # list[float | None]，长度和 tokens 一致
```

## 在 OPD 里算 teacher logprobs

OPD 中，teacher 只对 student **实际采样出来的** completion 打分。teacher 看到的必须是 `prompt + completion`，然后只截取 completion 区间的 logprobs。逐 token 相减要求 token 对齐——student 与 teacher 最好用同一 tokenizer。

```python
import numpy as np

def completion_teacher_logprobs(teacher_client, prompt_ids, completion_ids):
    all_ids = prompt_ids + completion_ids
    all_logprobs = teacher_client.compute_logprobs(
        prompt=trio.ModelInput.from_ints(all_ids),
    ).result()
    completion_logprobs = all_logprobs[len(prompt_ids):]
    if len(completion_logprobs) != len(completion_ids):
        raise ValueError("teacher logprobs and completion tokens are not aligned")
    if any(v is None for v in completion_logprobs):
        raise ValueError("completion logprobs should not contain None")
    return [float(v) for v in completion_logprobs]

student_logprobs = [float(v) for v in seq.logprobs]  # 旧策略对 completion 的 logprobs
teacher_logprobs = completion_teacher_logprobs(teacher_client, prompt_ids, list(seq.tokens))
reverse_kl = np.asarray(student_logprobs) - np.asarray(teacher_logprobs)
advantages = -kl_penalty_coef * reverse_kl
```

再把 `completion_ids`、student 采样时的 logprobs 和这里的 advantages 右移对齐，放进 `Datum.loss_fn_inputs` 用 `loss_fn="importance_sampling"` 训练。

## 异步与边界

- `sample_async()`、`compute_logprobs_async()` 一次 `await` 直接拿到结果，不要调用 `.result()`。
- 返回值里的 `None` 是正常的：第一个 token 没有前文条件。做 reward 或 loss 前要处理 `None`。

## 常见错误

- 把 `compute_logprobs` 当“生成 API”用：它不生成 token，只对给定序列打分。
- 想让 teacher 重新生成而非打分：OPD/OPSD 里 teacher 职责是**对 student 轨迹打分**，重新生成会破坏对齐。
- 直接按位置相减但 tokenizer 不同：student 与 teacher token 不一致会导致逐 token 差值无意义。
