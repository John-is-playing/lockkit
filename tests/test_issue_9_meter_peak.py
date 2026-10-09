import pytest
from lockkit import Meter, summarize


def test_peak_empty_returns_zero():
    """目标修复：空样本时 peak 应返回 0.0，修复前会抛 ValueError"""
    assert Meter().peak == 0.0


def test_summarize_empty_meter_peak():
    """目标修复：summarize 报表包含空 Meter 时不应崩溃，peak 应为 0.0"""
    report = summarize({"wait": Meter()})
    assert report["wait"]["peak"] == 0.0


def test_peak_non_empty_unchanged():
    """回归断言：非空时 peak 仍返回真实最大值，修复不得破坏此行为"""
    assert Meter().record(5).peak == 5.0


def test_empty_mean_valley_consistency():
    """回归断言：mean 和 valley 在空样本时本就返回 0.0，修复后须保持一致"""
    m = Meter()
    assert m.mean == 0.0
    assert m.valley == 0.0
