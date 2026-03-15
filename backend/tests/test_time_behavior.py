"""time_behavior モジュールのユニットテスト"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from time_behavior import get_time_period


class TestGetTimePeriod:
    def _make_dt(self, hour: int) -> datetime:
        return datetime(2026, 3, 15, hour, 0, 0)

    def test_朝6時(self):
        info = get_time_period(self._make_dt(6))
        assert info.period == "morning"
        assert info.response_rate > 0.7

    def test_昼12時(self):
        info = get_time_period(self._make_dt(12))
        assert info.period == "midday"
        assert info.response_rate < 0.7

    def test_夕方17時(self):
        info = get_time_period(self._make_dt(17))
        assert info.period == "evening"
        assert info.response_rate > 0.8

    def test_夜21時(self):
        info = get_time_period(self._make_dt(21))
        assert info.period == "night"
        assert info.response_rate > 0.8

    def test_深夜3時(self):
        info = get_time_period(self._make_dt(3))
        assert info.period == "midnight"
        assert info.response_rate < 0.3

    def test_全時間帯でlabelが設定されている(self):
        for hour in range(24):
            info = get_time_period(self._make_dt(hour))
            assert info.label != ""
            assert info.period in ("morning", "midday", "evening", "night", "midnight")
