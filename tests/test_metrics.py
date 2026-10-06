"""运行指标聚合。"""

from __future__ import annotations

from lockkit import Meter, summarize


def test_empty_meter_basics():
    meter = Meter()
    assert meter.count == 0
    assert meter.total == 0.0
    assert meter.mean == 0.0
    assert meter.valley == 0.0


def test_record_and_count():
    meter = Meter()
    meter.record(5)
    meter.record(7)
    assert meter.count == 2


def test_record_returns_self_for_chaining():
    meter = Meter().record(1).record(2)
    assert meter.count == 2


def test_extend_adds_samples():
    meter = Meter().extend([1, 2, 3])
    assert meter.count == 3


def test_total_and_mean():
    meter = Meter().extend([10, 20, 30])
    assert meter.total == 60
    assert meter.mean == 20.0


def test_peak_non_empty():
    meter = Meter().extend([10, 30, 20])
    assert meter.peak == 30


def test_valley_non_empty():
    meter = Meter().extend([10, 30, 20])
    assert meter.valley == 10


def test_len_and_iter():
    meter = Meter().extend([1, 2, 3])
    assert len(meter) == 3
    assert list(meter) == [1.0, 2.0, 3.0]


def test_sink_clears_samples():
    meter = Meter().extend([1, 2, 3])
    meter.sink()
    assert meter.count == 0
    assert meter.total == 0.0


def test_summarize_shape():
    report = summarize({"wait": Meter().extend([1, 3])})
    assert report["wait"]["count"] == 2
    assert report["wait"]["mean"] == 2.0
    assert report["wait"]["peak"] == 3.0


def test_summarize_multiple_meters():
    report = summarize({"a": Meter().record(5), "b": Meter().record(9)})
    assert set(report) == {"a", "b"}
    assert report["b"]["peak"] == 9.0


def test_summarize_empty_mapping():
    assert summarize({}) == {}
