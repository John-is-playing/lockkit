"""令牌桶限流器。"""

from __future__ import annotations

import time
from collections.abc import Callable

from .clock import system_clock


class TokenBucket:
    """令牌桶限流器。

    令牌以 ``rate`` 个/秒匀速补充，存量最多攒到 ``capacity`` 个。

    :param rate: 每秒补充的令牌数，必须为正
    :param capacity: 桶容量，默认等于 ``rate``，必须为正
    :param clock: 时间源，默认 :func:`time.monotonic`；测试可注入假时钟
    :raises ValueError: ``rate`` / ``capacity`` 非正

    示例::

        >>> bucket = TokenBucket(rate=10, capacity=3)
        >>> bucket.allow(3)
        True
        >>> bucket.allow(1)
        False
    """

    def __init__(
        self,
        rate: float,
        capacity: float | None = None,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate 必须为正数")
        cap = rate if capacity is None else capacity
        if cap <= 0:
            raise ValueError("capacity 必须为正数")

        self._rate = float(rate)
        self._capacity = float(cap)
        self._clock = clock or system_clock
        self._tokens = float(cap)
        self._updated = self._clock()

    @property
    def rate(self) -> float:
        return self._rate

    @property
    def capacity(self) -> float:
        return self._capacity

    def _refill(self) -> None:
        """按流逝的时间补充令牌，存量不超过容量。"""
        now = self._clock()
        elapsed = now - self._updated
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + self._rate * elapsed)
            self._updated = now

    def peek(self) -> float:
        """返回**当前**可用的令牌数，不消耗令牌。

        与 :meth:`allow` 一样先按流逝时间补充，只是不扣减。
        """
        return self._tokens

    def allow(self, n: float = 1) -> bool:
        """尝试取走 ``n`` 个令牌。

        可用令牌数**不少于** ``n`` 时取走并返回 ``True``（恰好取尽也算成功）；
        不足时不取走任何令牌并返回 ``False``。

        :raises ValueError: ``n`` 非正
        """
        if n <= 0:
            raise ValueError("n 必须为正数")

        self._refill()
        if self._tokens >= n:
            self._tokens -= n
            return True
        return False

    def __repr__(self) -> str:  # pragma: no cover - 调试用
        return f"TokenBucket(rate={self._rate}, capacity={self._capacity})"
