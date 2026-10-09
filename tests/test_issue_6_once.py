import pytest
from lockkit import Once


def test_once_failure_does_not_mark_done():
    """复现步骤1：首次调用失败后，done 状态应为 False"""
    once = Once()
    def failing_fn():
        raise ValueError("数据库还没起来")
    with pytest.raises(ValueError, match="数据库还没起来"):
        once.call(failing_fn)
    assert once.done is False, "失败后不应标记为已完成"


def test_once_failure_allows_retry():
    """复现步骤2：首次失败后，再次调用应重新执行并返回新结果"""
    once = Once()
    def failing_fn():
        raise ValueError("fail")
    with pytest.raises(ValueError):
        once.call(failing_fn)
    result = once.call(lambda: "初始化成功")
    assert result == "初始化成功", "失败后再次调用应返回实际执行结果，而非 None"


def test_once_calls_count_includes_failures():
    """期望修复断言：失败和成功调用都应计入 calls"""
    once = Once()
    def failing_fn():
        raise ValueError("fail")
    with pytest.raises(ValueError):
        once.call(failing_fn)
    once.call(lambda: "ok")
    assert once.calls == 2, "调用次数应累计失败和成功的调用"


def test_once_success_marks_done_and_caches():
    """回归断言：成功执行后标记为 done，后续调用直接返回缓存值且不重新执行"""
    once = Once()
    exec_count = 0
    def fn():
        nonlocal exec_count
        exec_count += 1
        return "cached_value"

    assert once.call(fn) == "cached_value"
    assert once.done is True
    assert once.calls == 1
    assert exec_count == 1

    assert once.call(fn) == "cached_value"
    assert exec_count == 1, "成功后再次调用不应重新执行函数"


def test_once_reset_clears_state():
    """回归断言：reset 应清空状态，允许重新执行"""
    once = Once()
    once.call(lambda: "first")
    assert once.done is True
    once.reset()
    assert once.done is False
    assert once.calls == 0
    assert once.call(lambda: "second") == "second"
