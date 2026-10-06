"""重试策略与重试执行。"""

from __future__ import annotations

import pytest

from lockkit import RetryPolicy, is_retryable, retry_call


# --- is_retryable ---------------------------------------------------------


def test_is_retryable_exact_match():
    assert is_retryable(ValueError("x"), (ValueError,)) is True


def test_is_retryable_non_match():
    assert is_retryable(ValueError("x"), (KeyError,)) is False


def test_is_retryable_instance_of_other_type():
    assert is_retryable(TypeError("x"), (ValueError,)) is False


def test_is_retryable_empty_tuple():
    assert is_retryable(ValueError("x"), ()) is False


# --- RetryPolicy.delay_for -------------------------------------------------


def test_delay_for_first_attempt_is_base():
    assert RetryPolicy(base_delay=1.0, factor=2.0).delay_for(1) == 1.0


def test_delay_grows_exponentially():
    policy = RetryPolicy(base_delay=1.0, factor=3.0)
    assert policy.delay_for(1) == 1.0
    assert policy.delay_for(2) == 3.0
    assert policy.delay_for(3) == 9.0


def test_delay_zero_base_is_zero():
    policy = RetryPolicy(base_delay=0.0, factor=2.0)
    assert policy.delay_for(3) == 0.0


def test_delay_rejects_attempt_below_one():
    policy = RetryPolicy()
    with pytest.raises(ValueError):
        policy.delay_for(0)


# --- RetryPolicy validation ------------------------------------------------


def test_policy_rejects_zero_attempts():
    with pytest.raises(ValueError):
        RetryPolicy(attempts=0)


def test_policy_rejects_negative_base_delay():
    with pytest.raises(ValueError):
        RetryPolicy(base_delay=-1.0)


def test_policy_rejects_non_positive_factor():
    with pytest.raises(ValueError):
        RetryPolicy(factor=0)


def test_policy_rejects_negative_max_delay():
    with pytest.raises(ValueError):
        RetryPolicy(max_delay=-1.0)


def test_policy_allows_none_max_delay():
    policy = RetryPolicy(max_delay=None)
    assert policy.max_delay is None


# --- RetryPolicy.should_retry ---------------------------------------------


def test_should_retry_exhausted_attempts():
    policy = RetryPolicy(attempts=2, retry_on=(ValueError,))
    assert policy.should_retry(ValueError("x"), attempt=2) is False


def test_should_retry_before_exhaustion():
    policy = RetryPolicy(attempts=3, retry_on=(ValueError,))
    assert policy.should_retry(ValueError("x"), attempt=1) is True


def test_should_retry_returns_false_for_unlisted_type():
    policy = RetryPolicy(attempts=3, retry_on=(ValueError,))
    assert policy.should_retry(KeyError("x"), attempt=1) is False


# --- retry_call ------------------------------------------------------------


def test_retry_call_returns_first_success():
    assert retry_call(lambda: 42) == 42


def test_retry_call_does_not_wait_on_success():
    seen: list[float] = []
    assert retry_call(lambda: "ok", sleep=seen.append) == "ok"
    assert seen == []


def test_retry_call_retries_then_succeeds():
    waits: list[float] = []
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("not yet")
        return "ok"

    policy = RetryPolicy(attempts=5, base_delay=1.0, factor=2.0, retry_on=(ValueError,))
    assert retry_call(flaky, policy, sleep=waits.append) == "ok"
    assert calls["n"] == 3
    assert waits == [1.0, 2.0]


def test_retry_call_reraises_after_exhaustion():
    def always_fail():
        raise ValueError("nope")

    policy = RetryPolicy(attempts=2, base_delay=0.0, retry_on=(ValueError,))
    with pytest.raises(ValueError):
        retry_call(always_fail, policy, sleep=lambda _: None)


def test_retry_call_does_not_retry_unlisted_type():
    calls = {"n": 0}

    def fail_with_key_error():
        calls["n"] += 1
        raise KeyError("boom")

    policy = RetryPolicy(attempts=5, base_delay=0.0, retry_on=(ValueError,))
    with pytest.raises(KeyError):
        retry_call(fail_with_key_error, policy, sleep=lambda _: None)
    assert calls["n"] == 1


def test_retry_call_skips_wait_when_delay_zero():
    waits: list[float] = []
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("x")
        return "ok"

    policy = RetryPolicy(attempts=3, base_delay=0.0, retry_on=(ValueError,))
    retry_call(flaky, policy, sleep=waits.append)
    assert waits == []
