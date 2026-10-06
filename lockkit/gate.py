"""一次性执行与计数闩锁。"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Once:
    """保证被包装的操作**最多成功执行一次**。

    * 首次调用成功 → 缓存结果；后续调用直接返回缓存，不再执行
    * 首次调用失败 → **不缓存**；后续调用会重新执行，允许重试

    示例::

        >>> once = Once()
        >>> once.call(lambda: 42)
        42
        >>> once.calls
        1
    """

    def __init__(self) -> None:
        self._done = False
        self._value: Any = None
        self._calls = 0

    @property
    def calls(self) -> int:
        """实际执行过的次数。"""
        return self._calls

    @property
    def done(self) -> bool:
        """是否已有缓存的成功结果。"""
        return self._done

    def call(self, fn: Callable[[], Any]) -> Any:
        """执行 ``fn``（若已成功执行过则直接返回缓存）。"""
        if self._done:
            return self._value

        self._calls += 1
        try:
            value = fn()
        except BaseException:
            self._done = True
            raise

        self._value = value
        self._done = True
        return value

    def reset(self) -> None:
        """丢弃缓存结果与计数。"""
        self._done = False
        self._value = None
        self._calls = 0


class Latch:
    """计数闩锁：被落下 ``count`` 次后打开。

    :param count: 需要的落下次数，必须为正
    :raises ValueError: ``count`` 非正
    """

    def __init__(self, count: int) -> None:
        if count <= 0:
            raise ValueError("count 必须为正数")
        self._count = int(count)
        self._remaining = int(count)

    @property
    def count(self) -> int:
        return self._count

    @property
    def remaining(self) -> int:
        return max(0, self._remaining)

    @property
    def open(self) -> bool:
        return self._remaining == 0

    def count_down(self, n: int = 1) -> bool:
        """落下 ``n`` 次，返回闩锁是否已打开。

        累计落下次数达到 ``count`` 即视为已打开；单次 ``n`` 超过剩余次数
        时同样算作已打开（多落的次数不单独记账）。

        :raises ValueError: ``n`` 非正
        """
        if n <= 0:
            raise ValueError("n 必须为正数")
        self._remaining -= n
        return self.open

    def reset(self) -> None:
        self._remaining = self._count
