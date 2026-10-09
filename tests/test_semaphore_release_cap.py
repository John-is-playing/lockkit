import pytest
from lockkit import Semaphore


def test_issue_release_exceeds_limit_single():
    """复现步骤：Semaphore(1)，acquire 1次，release 3次，available 应封顶为 1"""
    sem = Semaphore(1)
    assert sem.acquire() is True
    assert sem.available == 0

    sem.release()
    sem.release()
    sem.release()

    # 期望输出：1。修复前因 release() 无上限自增，实际为 3
    assert sem.available == 1


def test_issue_release_exceeds_limit_multiple():
    """多许可场景：Semaphore(3)，acquire 2次，release 5次，available 应封顶为 3"""
    sem = Semaphore(3)
    assert sem.acquire() is True
    assert sem.acquire() is True
    assert sem.available == 1

    for _ in range(5):
        sem.release()

    # 期望输出：3。修复前会变成 6
    assert sem.available == 3


def test_issue_release_without_acquire():
    """未借用直接多次归还：Semaphore(2)，release 10次，available 应封顶为 2"""
    sem = Semaphore(2)
    for _ in range(10):
        sem.release()

    # 期望输出：2。修复前会变成 10
    assert sem.available == 2


def test_regression_normal_lifecycle():
    """回归：正常借还循环不受影响，acquire 满后返回 False，release 正确恢复"""
    sem = Semaphore(2)
    assert sem.acquire() is True
    assert sem.acquire() is True
    assert sem.acquire() is False
    sem.release()
    assert sem.available == 1
    sem.release()
    assert sem.available == 2
    assert sem.acquire() is True
    assert sem.available == 1


def test_regression_initial_state_and_limit():
    """回归：初始状态与 limit 契约保持不变"""
    sem = Semaphore(5)
    assert sem.limit == 5
    assert sem.available == 5
