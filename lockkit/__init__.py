"""lockkit —— 一个用于演示 Fissue 的小型并发原语 / 资源管理工具库。

已发布的稳定功能：
    ManualClock       可手动推进的假时钟（测试用）
    TokenBucket       令牌桶限流器
    Semaphore         计数信号量
    ResourcePool      固定大小资源池
    RetryPolicy       重试策略（指数退避 + 封顶）
    retry_call        按策略重试执行
    is_retryable      判定异常是否可重试
    Once              最多成功执行一次
    Latch             计数闩锁
    Meter             运行指标聚合
    summarize         指标汇总

设计约定：凡是与时间有关的行为都接受一个 ``clock`` / ``sleep`` 注入点，
因此所有行为都能在不真正等待的前提下确定性复现。
"""

from .clock import ManualClock, system_clock
from .gate import Latch, Once
from .limiter import TokenBucket
from .metrics import Meter, summarize
from .pool import ResourcePool, Semaphore
from .retry import RetryPolicy, is_retryable, retry_call

__version__ = "0.7.0"

__all__ = [
    "ManualClock",
    "system_clock",
    "TokenBucket",
    "Semaphore",
    "ResourcePool",
    "RetryPolicy",
    "retry_call",
    "is_retryable",
    "Once",
    "Latch",
    "Meter",
    "summarize",
    "__version__",
]
