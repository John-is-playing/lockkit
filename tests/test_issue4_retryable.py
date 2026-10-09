import pytest
from lockkit import is_retryable, retry_call, RetryPolicy


def test_is_retryable_subclass_returns_true():
    # 目标用例：子类异常应被判定为可重试（修复前返回 False）
    assert is_retryable(TimeoutError("slow"), (OSError,)) is True


def test_is_retryable_unrelated_returns_false():
    # 回归断言：无关类型仍应返回 False
    assert is_retryable(ValueError("x"), (KeyError,)) is False


def test_is_retryable_exact_match_returns_true():
    # 回归断言：精确类型匹配仍应返回 True
    assert is_retryable(OSError("x"), (OSError,)) is True


def test_retry_call_retries_on_subclass():
    # 目标用例：retry_call 应对子类异常执行重试（修复前执行 1 次）
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        raise TimeoutError("still slow")

    with pytest.raises(TimeoutError):
        retry_call(
            flaky,
            RetryPolicy(attempts=3, base_delay=0.0, retry_on=(OSError,)),
            sleep=lambda _: None
        )
    assert calls["n"] == 3


def test_retry_call_no_retry_on_unrelated():
    # 回归断言：retry_call 对无关类型不应重试
    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        raise ValueError("bad")

    with pytest.raises(ValueError):
        retry_call(
            flaky,
            RetryPolicy(attempts=3, base_delay=0.0, retry_on=(KeyError,)),
            sleep=lambda _: None
        )
    assert calls["n"] == 1
