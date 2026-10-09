"""重试策略与重试执行。"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


def is_retryable(exc: BaseException, retry_on: tuple[type[BaseException], ...]) -> bool:
    """``exc`` 是否属于 ``retry_on`` 中列出的异常。

    判定包含**子类**：``retry_on=(OSError,)`` 时 ``TimeoutError`` 也应重试。
    """
    return type(exc) in retry_on


@dataclass(frozen=True)
class RetryPolicy:
    """重试策略。

    :param attempts: 总尝试次数（含首次），必须 >= 1
    :param base_delay: 首次重试前的等待秒数，不能为负
    :param factor: 退避倍数，必须为正
    :param max_delay: 单次等待的**上限**秒数（``None`` 表示不封顶）
    :param retry_on: 需要重试的异常类型（含其子类）
    :raises ValueError: 参数非法
    """

    attempts: int = 3
    base_delay: float = 1.0
    factor: float = 2.0
    max_delay: float | None = 30.0
    retry_on: tuple[type[BaseException], ...] = (Exception,)

    def __post_init__(self) -> None:
        if self.attempts < 1:
            raise ValueError("attempts 必须 >= 1")
        if self.base_delay < 0:
            raise ValueError("base_delay 不能为负数")
        if self.factor <= 0:
            raise ValueError("factor 必须为正数")
        if self.max_delay is not None and self.max_delay < 0:
            raise ValueError("max_delay 不能为负数")

    def delay_for(self, attempt: int) -> float:
        """返回第 ``attempt`` 次尝试失败后应等待的秒数（``attempt`` 从 1 起）。

        等待时间按 ``base_delay * factor ** (attempt - 1)`` 指数增长，
        但**超过 ``max_delay`` 时按 ``max_delay`` 截断**。

        :raises ValueError: ``attempt`` < 1
        """
        if attempt < 1:
            raise ValueError("attempt 从 1 起")
        delay = self.base_delay * (self.factor ** (attempt - 1))
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)
        return delay

    def should_retry(self, exc: BaseException, attempt: int) -> bool:
        """第 ``attempt`` 次尝试失败后，是否还应继续重试。"""
        if attempt >= self.attempts:
            return False
        return is_retryable(exc, self.retry_on)


def retry_call(
    fn: Callable[[], Any],
    policy: RetryPolicy | None = None,
    *,
    sleep: Callable[[float], None] | None = None,
) -> Any:
    """按策略反复调用 ``fn``，直到成功或耗尽尝试次数。

    :param fn: 无参可调用对象
    :param policy: 重试策略，默认 :class:`RetryPolicy`
    :param sleep: 等待函数（秒），默认 :func:`time.sleep`；
        测试时可注入一个只记录时长的假实现，避免真正等待
    :returns: 首次成功调用的返回值
    :raises: 最后一次尝试抛出的异常
    """
    active = policy or RetryPolicy()
    waiter = sleep if sleep is not None else time.sleep

    attempt = 1
    while True:
        try:
            return fn()
        except BaseException as exc:
            if attempt >= active.attempts or not is_retryable(exc, active.retry_on):
                raise
            delay = active.delay_for(attempt)
            if delay > 0:
                waiter(delay)
            attempt += 1
