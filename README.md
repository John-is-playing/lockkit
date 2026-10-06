# lockkit

一个刻意设计的**小型并发原语 / 资源管理工具库**，用来真实验证 Fissue 的完整链路：

抓取 → AI 评测 → 生成验证器 → 沙盒 F2P 验证 → 自动修复提 PR。

## 为什么是「第四个领域」

| 夹具 | 领域 | 考什么 |
|---|---|---|
| `textkit` | 文本处理 | 单函数语义 |
| `ratekit` | 金额 / 费率 | 数值边界 |
| `pipekit` | 分片流水线 / 区间 | 跨模块调用链 |
| `envkit` | 配置 / 缓存 / 校验 | 状态副作用、环境依赖、输入校验 |
| **`lockkit`** | **并发原语 / 资源管理** | **资源不变量、超时上限、一次性语义** |

它回答的问题是：

> **当缺陷不再表现为「算错一个数」，而是「资源不变量被悄悄破坏」、
> 「本该封顶的等待无限增长」、「本该只成功一次的语义变成了缓存失败」时，
> Fissue 还能不能构造出稳定的最小复现，并给出正确的定论？**

## 公开 API

| 函数 / 类 | 说明 |
|---|---|
| `ManualClock(start)` | 可手动推进的假时钟（测试用） |
| `TokenBucket(rate, capacity, clock=…)` | 令牌桶限流器 |
| `Semaphore(permits)` | 计数信号量（归还不得超过初始许可数） |
| `ResourcePool(size, factory)` | 固定大小资源池 |
| `RetryPolicy(attempts, base_delay, factor, max_delay, retry_on)` | 重试策略 |
| `retry_call(fn, policy, sleep=…)` | 按策略重试执行 |
| `is_retryable(exc, retry_on)` | 判定异常是否可重试（含子类） |
| `Once()` | 最多**成功**执行一次 |
| `Latch(count)` | 计数闩锁 |
| `LockSet(*semaphores)` | **有序加锁集**：按稳定 key 排序后统一加锁，避免死锁 |
| `Meter()` | 运行指标聚合 |

## 有序加锁集（LockSet）

多个锁需要同时持有时，只要加锁顺序不一致就会死锁。`LockSet` 按稳定 key
排序后统一加锁，并在拿不到任意一个时**回滚已拿到的许可**：

```python
from lockkit.lockset import LockSet

with LockSet(sem_a, sem_b, sem_c) as acquired:
    # 内部按稳定 key 排序后统一加锁，拿不到任意一个时回滚已拿到的许可
    ...
```

因此无论调用方以什么顺序传入，实际加锁顺序都是一致的，可从根本上避免死锁。

详见 `lockkit/lockset.py`（随本次变更提供）。

> 本库所有与时间有关的行为都接受 `clock` / `sleep` 注入点，
> 因此无需真正等待即可确定性复现——这是它在沙盒里能被稳定验证的前提。

## 本地自检

```bash
cd demo/lockkit/repo
python -m pytest -q            # 基线应 74 passed
```

> 基线测试**刻意不覆盖**植入的缺陷路径——缺陷藏在没被覆盖的分支上，
> 逼 Fissue 真正去「读代码 → 写验证器 → 跑 F2P」，而不是抄现成测试。

## 目录

```
demo/lockkit/
├── repo/           待推送的测试仓库（独立 git 仓库）
├── fixtures/       15 个 Issue 的内容与元数据
├── scripts/        一键建仓库 / 建 Issue / 建 PR
└── README.md       设计意图与期望结果对照表（见上一级目录）
```
