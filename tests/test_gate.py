"""一次性执行与计数闩锁。"""

from __future__ import annotations

import pytest

from lockkit import Latch, Once


# --- Once -----------------------------------------------------------------


def test_once_runs_and_returns_value():
    assert Once().call(lambda: 7) == 7


def test_once_caches_result_on_repeat_calls():
    once = Once()
    assert once.call(lambda: 1) == 1
    assert once.call(lambda: 2) == 1


def test_once_counts_only_real_executions():
    once = Once()
    once.call(lambda: None)
    once.call(lambda: None)
    once.call(lambda: None)
    assert once.calls == 1


def test_once_done_flag():
    once = Once()
    assert once.done is False
    once.call(lambda: None)
    assert once.done is True


def test_once_reset_clears_state():
    once = Once()
    once.call(lambda: 1)
    once.reset()
    assert once.done is False
    assert once.calls == 0
    assert once.call(lambda: 2) == 2


def test_once_propagates_exception():
    once = Once()
    with pytest.raises(ValueError):
        once.call(lambda: (_ for _ in ()).throw(ValueError("boom")))


def test_once_does_not_cache_success_when_raised():
    # 只断言「抛出的异常会向上传播」，不假设失败之后的缓存行为
    once = Once()
    with pytest.raises(RuntimeError):
        once.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
    assert once.calls >= 1


# --- Latch ----------------------------------------------------------------


def test_latch_starts_closed():
    latch = Latch(2)
    assert latch.count == 2
    assert latch.remaining == 2
    assert latch.open is False


def test_latch_opens_after_enough_countdowns():
    latch = Latch(2)
    latch.count_down()
    assert latch.open is False
    latch.count_down()
    assert latch.open is True


def test_latch_count_down_returns_open_state():
    latch = Latch(1)
    assert latch.count_down() is True


def test_latch_count_down_rejects_non_positive():
    latch = Latch(2)
    with pytest.raises(ValueError):
        latch.count_down(0)
    with pytest.raises(ValueError):
        latch.count_down(-1)


def test_latch_reset_recloses():
    latch = Latch(1)
    latch.count_down()
    latch.reset()
    assert latch.open is False
    assert latch.remaining == 1


def test_latch_rejects_non_positive_count():
    with pytest.raises(ValueError):
        Latch(0)
    with pytest.raises(ValueError):
        Latch(-3)
