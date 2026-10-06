"""信号量与资源池。"""

from __future__ import annotations

import pytest

from lockkit import ResourcePool, Semaphore


# --- Semaphore ------------------------------------------------------------


def test_semaphore_initial_state():
    sem = Semaphore(3)
    assert sem.limit == 3
    assert sem.available == 3


def test_semaphore_acquire_decrements():
    sem = Semaphore(2)
    assert sem.acquire() is True
    assert sem.available == 1


def test_semaphore_acquire_when_empty():
    sem = Semaphore(1)
    sem.acquire()
    assert sem.acquire() is False
    assert sem.available == 0


def test_semaphore_zero_permits():
    sem = Semaphore(0)
    assert sem.available == 0
    assert sem.acquire() is False


def test_semaphore_balanced_release_restores():
    sem = Semaphore(2)
    sem.acquire()
    sem.acquire()
    sem.release()
    sem.release()
    assert sem.available == 2


def test_semaphore_rejects_negative():
    with pytest.raises(ValueError):
        Semaphore(-1)


def test_semaphore_hold_context_manager():
    sem = Semaphore(1)
    with sem.hold() as held:
        assert held is sem
        assert sem.available == 0
    assert sem.available == 1


def test_semaphore_hold_raises_when_exhausted():
    sem = Semaphore(1)
    sem.acquire()
    with pytest.raises(RuntimeError):
        with sem.hold():
            pass  # pragma: no cover


# --- ResourcePool ---------------------------------------------------------


def _make_pool(size: int = 2):
    return ResourcePool(size, lambda: object())


def test_pool_creates_requested_items():
    pool = _make_pool(3)
    assert pool.size == 3
    assert pool.available == 3
    assert pool.in_use == 0


def test_pool_acquire_returns_item_and_marks_in_use():
    pool = _make_pool(2)
    item = pool.acquire()
    assert item is not None
    assert pool.available == 1
    assert pool.in_use == 1


def test_pool_acquire_when_exhausted_returns_none():
    pool = _make_pool(1)
    assert pool.acquire() is not None
    assert pool.acquire() is None


def test_pool_release_returns_item_to_free_list():
    pool = _make_pool(1)
    item = pool.acquire()
    pool.release(item)
    assert pool.available == 1
    assert pool.acquire() is item


def test_pool_release_twice_does_not_duplicate():
    pool = _make_pool(1)
    item = pool.acquire()
    pool.release(item)
    pool.release(item)
    assert pool.available == 1


def test_pool_release_foreign_item_raises():
    pool = _make_pool(1)
    with pytest.raises(ValueError):
        pool.release(object())


def test_pool_borrow_returns_item_and_restores():
    pool = _make_pool(1)
    with pool.borrow() as item:
        assert item is not None
        assert pool.available == 0
    assert pool.available == 1


def test_pool_borrow_raises_when_exhausted():
    pool = _make_pool(1)
    with pool.borrow():
        with pytest.raises(RuntimeError):
            with pool.borrow():
                pass  # pragma: no cover


def test_pool_rejects_non_positive_size():
    with pytest.raises(ValueError):
        ResourcePool(0, lambda: None)
    with pytest.raises(ValueError):
        ResourcePool(-2, lambda: None)


def test_pool_rejects_non_callable_factory():
    with pytest.raises(TypeError):
        ResourcePool(1, "not-callable")
