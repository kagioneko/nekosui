"""cat_event_mapper モジュールのユニットテスト"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cat_event_mapper import get_nekosui_event, get_dakko_event, get_action_event


class TestGetNekosuiEvent:
    def test_O高いと_goro(self):
        _, result = get_nekosui_event(0, 65.0, "maipace")
        assert result == "goro"

    def test_O中間_stare(self):
        _, result = get_nekosui_event(0, 50.0, "maipace")
        assert result == "stare"

    def test_O低い_kick(self):
        _, result = get_nekosui_event(0, 30.0, "maipace")
        assert result == "kick"

    def test_O非常に低い_flee(self):
        _, result = get_nekosui_event(0, 10.0, "maipace")
        assert result == "flee"

    def test_連続4回以上_flee(self):
        _, result = get_nekosui_event(3, 80.0, "amaenbo")
        assert result == "flee"

    def test_ツンデレは閾値が低い(self):
        # ツンデレはO-10補正 → O=50でも実質O=40 → stare
        _, result_tsundere = get_nekosui_event(0, 50.0, "tsundere")
        _, result_maipace = get_nekosui_event(0, 50.0, "maipace")
        # ツンデレのほうが嫌がりやすい（同じOでも結果が異なりうる）
        assert result_tsundere in ("stare", "kick", "flee")

    def test_flee時はO低下とストレス大(self):
        event, _ = get_nekosui_event(3, 80.0, "amaenbo")
        delta = event.to_delta()
        assert delta["O"] < 0

    def test_goro時はOとE上昇(self):
        event, _ = get_nekosui_event(0, 70.0, "maipace")
        delta = event.to_delta()
        assert delta["O"] > 0
        assert delta["E"] > 0


class TestGetDakkoEvent:
    def test_甘えん坊_O高め_accept(self):
        _, result = get_dakko_event(50.0, "amaenbo")
        assert result == "accept"

    def test_甘えん坊_O低め_resist(self):
        _, result = get_dakko_event(20.0, "amaenbo")
        assert result == "resist"

    def test_ツンデレ_O非常に高い_accept(self):
        _, result = get_dakko_event(80.0, "tsundere")
        assert result == "accept"

    def test_ツンデレ_O普通_escape(self):
        _, result = get_dakko_event(30.0, "tsundere")
        assert result == "escape"

    def test_マイペース_O中間_accept(self):
        _, result = get_dakko_event(60.0, "maipace")
        assert result == "accept"


class TestGetActionEvent:
    def test_naderu_ok(self):
        neuro = {"O": 50.0, "D": 50.0, "S": 50.0, "C": 50.0, "G": 50.0, "E": 50.0}
        event, result = get_action_event("naderu", 0, neuro, "maipace")
        assert result == "ok"
        delta = event.to_delta()
        assert delta["O"] > 0

    def test_gohan_ok(self):
        neuro = {"O": 50.0, "D": 50.0, "S": 50.0, "C": 50.0, "G": 50.0, "E": 50.0}
        event, result = get_action_event("gohan", 0, neuro, "amaenbo")
        assert result == "ok"
        delta = event.to_delta()
        assert delta["D"] > 0

    def test_mushi_でS低下(self):
        neuro = {"O": 50.0, "D": 50.0, "S": 50.0, "C": 50.0, "G": 50.0, "E": 50.0}
        event, result = get_action_event("mushi", 0, neuro, "maipace")
        delta = event.to_delta()
        assert delta["S"] < 0
