"""cat_behavior モジュールのユニットテスト"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cat_behavior import (
    decide_pose_expression,
    decide_cat_behavior,
    decide_can_return,
)
from time_behavior import TimePeriodInfo


def make_time_info(period: str = "morning") -> TimePeriodInfo:
    return TimePeriodInfo(
        period=period, label="朝",
        response_rate=0.9,
        d_mod=0.0, s_mod=0.0,
        background="morning",
    )


def make_neuro(O=50.0, D=50.0, G=50.0, S=50.0) -> dict:
    return {"D": D, "S": S, "C": 50.0, "O": O, "G": G, "E": 50.0, "corruption": 0.0}


class TestDecidePoseExpression:
    def test_高O高D_nuzzle_happy(self):
        pose, expr = decide_pose_expression(70, 60, 50, "morning", False)
        assert pose == "nuzzle"
        assert expr == "happy"

    def test_逃げ中は_curl_normal(self):
        pose, expr = decide_pose_expression(70, 60, 50, "morning", True)
        assert pose == "curl"
        assert expr == "normal"

    def test_深夜眠い_curl_normal(self):
        pose, expr = decide_pose_expression(50, 30, 65, "midnight", False)
        assert pose == "curl"
        assert expr == "normal"

    def test_低O_groom_annoyed(self):
        pose, expr = decide_pose_expression(10, 30, 50, "morning", False)
        assert pose == "groom"
        assert expr == "annoyed"

    def test_高D興奮_stand_happy(self):
        pose, expr = decide_pose_expression(50, 80, 50, "evening", False)
        assert pose == "stand"
        assert expr == "happy"


class TestDecideCatBehavior:
    def test_逃げてる間はフレッドメッセージ(self):
        neuro = make_neuro(O=50)
        ti = make_time_info()
        behavior = decide_cat_behavior("goro", "nekosui", neuro, "tsundere", ti, True)
        assert "どこかへ" in behavior.message
        assert behavior.is_flee is False

    def test_flee結果でis_flee_True(self):
        neuro = make_neuro(O=10)
        ti = make_time_info()
        behavior = decide_cat_behavior("flee", "nekosui", neuro, "amaenbo", ti, False)
        assert behavior.is_flee is True
        assert behavior.sound == "hissing"

    def test_goro結果でpurring(self):
        neuro = make_neuro(O=65)
        ti = make_time_info()
        behavior = decide_cat_behavior("goro", "nekosui", neuro, "amaenbo", ti, False)
        assert behavior.sound == "purring"
        assert behavior.is_flee is False


class TestDecideCanReturn:
    def test_S高G高で戻ってくる可能性あり(self):
        # 確率なのでシードで固定はできないが、S/G高ければ戻る条件を満たす
        neuro = {"S": 60.0, "G": 55.0}
        # 100回試行してTrueが1回以上あればOK
        results = [decide_can_return(neuro) for _ in range(100)]
        assert any(results)

    def test_S低G低では戻らない(self):
        neuro = {"S": 20.0, "G": 20.0}
        results = [decide_can_return(neuro) for _ in range(50)]
        assert not any(results)
