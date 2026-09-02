---
name: workflow-improver
description: 读取仓库 docs/agent-feedback/ 中 open 反馈，对照 base skill（AGENTS.md/CLAUDE.md）聚类并提议最小编辑，输出提案文档供用户审阅。触发词："跑一下 improver"、"整理反馈"、"改进一下 skill"。
---

# Workflow Improver（反馈改进器）

职责：把积累的反馈"编译"成对 base skill 的最小编辑提案。只提议，不自动合入。

## 触发

按需触发，用户说"跑一下 improver / 整理反馈 / 改进一下 skill"；试点期不做定时调度。

## 流程

1. 收集：读取当前仓库（或用户指定的全部试点仓库）docs/agent-feedback/*.md 中 status: open 的条目。
2. 聚类：按 category × base skill 章节分组。
3. 对每簇提议最小编辑：
   - 原则优先（写原则不写规则），每条给 why；
   - 置信度：高 / 需确认（拿不准标需确认，不强提议）；
   - 实验数字类反馈不进入 skill 编辑，转 worklog。
4. 输出提案：docs/agent-feedback/proposals/YYYY-MM-DD.md，每项含：
   - 触发反馈 id；现状（base skill 当前写法或缺失）；建议 diff（before/after）；理由；置信度。
5. 用户审阅：批准 → 应用；拒绝 → 条目标记 rejected + 理由。

## 应用规则（仅在用户批准后执行）

- AGENTS.md 与 CLAUDE.md 同时修改：bimsa_life 保持字节一致；coupled_jj 追加内容相同的小节（存量差异 deferred）；
- 最小 diff，不顺手重构；
- 应用后：条目 status=applied、更新 README 状态、docs/worklog.md 记一条；
- 自查：双文件一致（bimsa_life 用 Compare-Object 无差异；coupled_jj 验证追加小节逐字相同）、格式与触发词覆盖。

## 守门

- 假设反馈会错：对照 base skill 现状与仓库事实 sanity-check，不确定就 needs-confirm；
- 只有显式纠正算信号，点赞/模糊好评不算；
- 人类在环：提案永远先给人看，不自动合入。
