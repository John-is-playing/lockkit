"""信号量与资源池。"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any


class Semaphore:
    """计数信号量。

    许可数在创建时固定；``release()`` 归还的许可**不得**使可用数
    超过初始许可数。

    :param permits: 初始许可数，必须非负
    :raises ValueError: ``permits`` 为负
    """

    def __init__(self, permits: int) -> None:
        if permits < 0:
            raise ValueError("permits 不能为负数")
        self._limit = int(permits)
        self._available = int(permits)

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def available(self) -> int:
        return self._available

    def acquire(self) -> bool:
        """取一个许可；无可用许可时返回 ``False``。"""
        if self._available > 0:
            self._available -= 1
            return True
        return False

    def release(self) -> None:
        """归还一个许可。"""
        self._available += 1

    @contextmanager
    def hold(self) -> Iterator["Semaphore"]:
        """上下文管理器：进入时取许可，退出时归还。

        :raises RuntimeError: 没有可用许可
        """
        if not self.acquire():
            raise RuntimeError("没有可用许可")
        try:
            yield self
        finally:
            self.release()


class ResourcePool:
    """固定大小的资源池。

    :param size: 资源数量，必须为正
    :param factory: 无参工厂，用于创建每个资源
    :raises ValueError: ``size`` 非正
    :raises TypeError: ``factory`` 不可调用
    """

    def __init__(self, size: int, factory: Callable[[], Any]) -> None:
        if size <= 0:
            raise ValueError("size 必须为正数")
        if not callable(factory):
            raise TypeError("factory 必须可调用")

        self._items = [factory() for _ in range(int(size))]
        self._free = list(self._items)

    @property
    def size(self) -> int:
        return len(self._items)

    @property
    def available(self) -> int:
        return len(self._free)

    @property
    def in_use(self) -> int:
        return self.size - self.available

    def acquire(self) -> Any:
        """取一个空闲资源；没有空闲时返回 ``None``。"""
        if not self._free:
            return None
        return self._free.pop()

    def release(self, item: Any) -> None:
        """归还一个资源。

        :raises ValueError: ``item`` 不属于本池
        """
        if not any(item is owned for owned in self._items):
            raise ValueError("不是本池的资源")
        if not any(item is owned for owned in self._free):
            self._free.append(item)

    @contextmanager
    def borrow(self) -> Iterator[Any]:
        """借出一个资源，退出时自动归还。

        :raises RuntimeError: 资源池已耗尽
        """
        item = self.acquire()
        if item is None:
            raise RuntimeError("资源池已耗尽")
        yield item
        self.release(item)
