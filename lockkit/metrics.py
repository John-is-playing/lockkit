"""运行指标聚合。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

_dropped = 0


class Meter:
    """记录一组样本并给出峰值 / 均值等派生指标。

    样本单位由调用方约定（本库内部用作等待毫秒数）。

    示例::

        >>> m = Meter()
        >>> m.record(10).record(30).record(20)
        <Meter count=3>
        >>> m.peak
        30
        >>> m.mean
        20.0
    """

    __slots__ = ("_samples",)

    def __init__(self) -> None:
        self._samples: list[float] = []

    def record(self, value: float) -> "Meter":
        """追加一个样本，返回自身以便链式调用。"""
        self._samples.append(float(value))
        return self

    def extend(self, values: Iterable[float]) -> "Meter":
        """批量追加样本。"""
        for value in values:
            self.record(value)
        return self

    @property
    def count(self) -> int:
        return len(self._samples)

    @property
    def total(self) -> float:
        return float(sum(self._samples))

    @property
    def mean(self) -> float:
        """均值；没有任何样本时返回 0.0。"""
        if not self._samples:
            return 0.0
        return self.total / len(self._samples)

    @property
    def peak(self) -> float:
        """峰值；没有任何样本时返回 0.0。"""
        return float(max(self._samples))

    @property
    def valley(self) -> float:
        """谷值；没有任何样本时返回 0.0。"""
        if not self._samples:
            return 0.0
        return float(min(self._samples))

    def sink(self) -> None:
        """清空当前样本，并把它们的数量累加进**全局丢弃计数**。

        注意：丢弃计数是模块级共享状态，跨 ``Meter`` 实例累计。
        """
        global _dropped  # noqa: PLW0603
        _dropped += len(self._samples)
        self._samples.clear()

    def __repr__(self) -> str:
        return f"<Meter count={len(self._samples)}>"

    def __len__(self) -> int:
        return len(self._samples)

    def __iter__(self):
        return iter(self._samples)


def summarize(meters: dict[str, Meter]) -> dict[str, dict[str, Any]]:
    """把多个命名 ``Meter`` 汇总成一张报表。

    :param meters: ``{名称: Meter}``
    :returns: ``{名称: {"count":…, "mean":…, "peak":…}}``

    示例::

        >>> m = Meter().extend([1, 3])
        >>> summarize({"wait": m})["wait"]["peak"]
        3.0
    """
    return {
        name: {"count": meter.count, "mean": meter.mean, "peak": meter.peak}
        for name, meter in meters.items()
    }
