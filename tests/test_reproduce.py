import pytest
from lockkit.retry import RetryPolicy


def test_delay_for_capped_at_max_delay():
    """复现 Issue #3：max_delay=5.0 时，delay_for 必须截断，不能无限增长"""
    policy = RetryPolicy(attempts=8, base_delay=1.0, factor=2.0, max_delay=5.0)
    assert policy.delay_for(1) == 1.0
    assert policy.delay_for(2) == 2.0
    assert policy.delay_for(3) == 4.0
    assert policy.delay_for(4) == 5.0
    assert policy.delay_for(5) == 5.0
    assert policy.delay_for(6) == 5.0


def test_delay_for_high_attempt_stays_capped():
    """期望修复中明确提到的用例：attempt=10 时仍为 5.0"""
    policy = RetryPolicy(attempts=12, base_delay=1.0, factor=2.0, max_delay=5.0)
    assert policy.delay_for(10) == 5.0


def test_delay_for_unbounded_when_max_delay_is_none():
    """回归断言：max_delay=None 时保持原有指数退避行为，不封顶"""
    policy = RetryPolicy(attempts=10, base_delay=1.0, factor=2.0, max_delay=None)
    assert policy.delay_for(1) == 1.0
    assert policy.delay_for(4) == 8.0
    assert policy.delay_for(10) == 512.0


def test_delay_for_invalid_attempt_raises_value_error():
    """回归断言：attempt < 1 必须抛出 ValueError，修复不能破坏输入校验"""
    policy = RetryPolicy(attempts=5, base_delay=1.0, factor=2.0, max_delay=5.0)
    with pytest.raises(ValueError, match="attempt 从 1 起"):
        policy.delay_for(0)
