"""可控时钟。"""

from __future__ import annotations

import pytest

from lockkit import ManualClock, system_clock


def test_manual_clock_starts_at_zero():
    assert ManualClock()() == 0.0


def test_manual_clock_accepts_start():
    assert ManualClock(12.5)() == 12.5


def test_manual_clock_is_callable_without_args():
    clk = ManualClock()
    assert clk() == clk()


def test_tick_advances_time():
    clk = ManualClock(1.0)
    clk.tick(2.5)
    assert clk() == 3.5


def test_tick_accepts_zero():
    clk = ManualClock(4.0)
    clk.tick(0)
    assert clk() == 4.0


def test_tick_returns_self_for_chaining():
    clk = ManualClock()
    assert clk.tick(1).tick(2)() == 3.0


def test_tick_rejects_negative():
    clk = ManualClock()
    with pytest.raises(ValueError):
        clk.tick(-1)


def test_instances_are_independent():
    a, b = ManualClock(), ManualClock()
    a.tick(5)
    assert a() == 5.0
    assert b() == 0.0


def test_system_clock_is_non_decreasing():
    first = system_clock()
    second = system_clock()
    assert isinstance(first, float)
    assert second >= first
