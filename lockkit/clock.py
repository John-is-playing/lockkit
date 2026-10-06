"""可控时钟。

本库所有与时间相关的行为（限流补充、退避等待）都通过一个
``Callable[[], float]`` 时间源取值，默认是 :func:`time.monotonic`。
测试时注入 :class:`ManualClock`，即可在不真正 sleep 的情况下
确定性地观察时间推进带来的行为变化。
"""

from __future__ import annotations

import time


def system_clock() -> float:
    """默认时间源：单调时钟。"""
    return time.monotonic()


class ManualClock:
    """可手动推进的时钟。

    :param start: 起始读数（秒）

    示例::

        >>> clk = ManualClock()
        >>> clk()
        0.0
        >>> clk.tick(2.5)()
        2.5
    """

    __slots__ = ("now",)

    def __init__(self, start: float = 0.0) -> None:
        self.now = float(start)

    def __call__(self) -> float:
        return self.now

    def tick(self, seconds: float) -> "ManualClock":
        """把时钟向前推进 ``seconds`` 秒，返回自身以便链式调用。"""
        if seconds < 0:
            raise ValueError("seconds 不能为负数")
        self.now += float(seconds)
        return self
