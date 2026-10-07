"""令牌桶限流器。"""

from __future__ import annotations

import pytest

from lockkit import ManualClock, TokenBucket


def test_starts_with_full_capacity():
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.peek() == 3


def test_capacity_defaults_to_rate():
    bucket = TokenBucket(rate=7)
    assert bucket.capacity == 7
    assert bucket.peek() == 7


def test_rate_property_exposed():
    assert TokenBucket(rate=2, capacity=5).rate == 2


def test_take_below_capacity_succeeds():
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(2) is True


def test_take_more_than_available_fails():
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(4) is False


def test_failed_take_does_not_consume_tokens():
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(4) is False
    assert bucket.allow(2) is True


def test_refill_after_elapsed_time():
    clk = ManualClock()
    bucket = TokenBucket(rate=10, capacity=3, clock=clk)
    bucket.allow(2)
    clk.tick(1.0)
    # 秒补充 10 个，早已超过容量，因此至少还能再取 2 个
    assert bucket.allow(2) is True


def test_refill_never_exceeds_capacity():
    clk = ManualClock()
    bucket = TokenBucket(rate=10, capacity=3, clock=clk)
    assert bucket.allow(2) is True
    clk.tick(100)
    assert bucket.allow(2) is True
    assert bucket.allow(2) is False


def test_peek_does_not_consume():
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.peek() == bucket.peek()


def test_peek_reflects_taken_tokens():
    bucket = TokenBucket(rate=10, capacity=3)
    bucket.allow(2)
    assert bucket.peek() == 1


def test_exact_drain_succeeds():
    """可用令牌恰好等于 n 时应取尽成功（边界）。"""
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(3) is True
    assert bucket.peek() == 0


def test_take_after_exact_drain_fails():
    """取尽之后再取就真的没有了。"""
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(3) is True
    assert bucket.allow(1) is False


def test_allow_rejects_non_positive():
    bucket = TokenBucket(rate=10, capacity=3)
    with pytest.raises(ValueError):
        bucket.allow(0)
    with pytest.raises(ValueError):
        bucket.allow(-1)


def test_rejects_non_positive_rate():
    with pytest.raises(ValueError):
        TokenBucket(rate=0)
    with pytest.raises(ValueError):
        TokenBucket(rate=-2)


def test_rejects_non_positive_capacity():
    with pytest.raises(ValueError):
        TokenBucket(rate=1, capacity=0)
    with pytest.raises(ValueError):
        TokenBucket(rate=1, capacity=-3)
