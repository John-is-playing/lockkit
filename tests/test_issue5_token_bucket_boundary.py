import pytest
from lockkit import TokenBucket


def test_allow_exact_capacity_succeeds():
    """复现 Issue #5：恰好取尽全部令牌时应成功"""
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.peek() == 3, "初始令牌应等于容量"
    assert bucket.allow(3) is True, "allow(3) 在恰好等于容量时应返回 True"
    assert bucket.peek() == 0, "取尽后剩余令牌应为 0"


def test_allow_exhausted_fails():
    """取尽后再次请求应失败"""
    bucket = TokenBucket(rate=10, capacity=3)
    bucket.allow(3)
    assert bucket.allow(1) is False, "令牌为 0 时 allow(1) 应返回 False"


def test_allow_insufficient_no_deduction():
    """回归断言：不足时不扣减任何令牌并返回 False"""
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(4) is False
    assert bucket.peek() == 3, "请求超过容量时不应扣减令牌"


def test_allow_partial_succeeds():
    """回归断言：正常部分取用应成功"""
    bucket = TokenBucket(rate=10, capacity=3)
    assert bucket.allow(2) is True
    assert bucket.peek() == 1


def test_allow_non_positive_raises():
    """回归断言：非正数参数应抛出 ValueError"""
    bucket = TokenBucket(rate=10, capacity=3)
    with pytest.raises(ValueError):
        bucket.allow(0)
    with pytest.raises(ValueError):
        bucket.allow(-1)
