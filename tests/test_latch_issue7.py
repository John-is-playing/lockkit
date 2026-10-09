import pytest
from lockkit.gate import Latch


def test_issue7_over_count_down_opens_latch():
    """精确复现 Issue #7：单次 count_down 超过剩余次数时 open 状态错乱"""
    latch = Latch(2)
    assert latch.remaining == 2
    assert latch.open is False

    result = latch.count_down(5)
    assert result is True, "count_down 返回值应为 True（表示闩锁已打开）"
    assert latch.remaining == 0, "remaining 对外必须裁剪为 0"
    assert latch.open is True, "open 应在累计落下 >= count 时返回 True（修复前因 _remaining 为负数而返回 False）"


def test_issue7_under_count_down_stays_closed():
    """回归断言：未达阈值时保持关闭，且返回值正确（对应正文期望修复示例）"""
    latch2 = Latch(3)
    result = latch2.count_down(1)
    assert result is False, "未达阈值时 count_down 应返回 False"
    assert latch2.open is False, "未达阈值时 open 必须为 False"
    assert latch2.remaining == 2


def test_regression_exact_threshold_and_sequential():
    """回归断言：精确达到阈值与逐次 count_down 的既有行为不受影响"""
    latch3 = Latch(2)
    assert latch3.count_down(2) is True
    assert latch3.open is True
    assert latch3.remaining == 0

    latch4 = Latch(3)
    assert latch4.count_down(1) is False
    assert latch4.count_down(1) is False
    assert latch4.count_down(1) is True
    assert latch4.open is True
