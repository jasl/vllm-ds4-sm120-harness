---
id: ZH-WR-TECH-001
tags: writing, subjective, benchmark-suite, technical_article
task_type: writing
language: zh-CN
category: technical_article
source: gpt-pro-llm-benchmark-prompt-suite
max_tokens: 4096
temperature: 1.0
top_p: 1.0
min_chars: 500
---
请写一篇约900—1200字的中文技术文章，题目自拟，面向有一年以上经验的前端/全栈工程师。主题：如何设计“离线优先”的轻量级任务管理 Web 应用。

必须覆盖：
1. 为什么离线优先不只是“断网也能用”，还涉及用户信任与数据一致性。
2. IndexedDB、Service Worker、后台同步/重试队列各自承担什么职责。
3. 至少两类冲突场景，例如同一任务在多端被编辑、离线删除与在线更新交叉。
4. 一个简化的数据流：本地写入、排队、同步、确认、失败回滚或重试。
5. 讨论可观测性：如何记录同步失败、冲突率、平均恢复时间。

要求：语言清晰，不要堆砌术语；不要写代码；最后用3条项目落地建议收束。
