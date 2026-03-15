"""cat_initializer モジュールのユニットテスト"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cat_initializer import (
    create_new_cat,
    generate_birthday,
    generate_initial_neuro_state,
)


class TestGenerateBirthday:
    def test_形式がMM_DD(self):
        bd = generate_birthday()
        parts = bd.split("-")
        assert len(parts) == 2
        month, day = int(parts[0]), int(parts[1])
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_複数回生成でばらつきあり(self):
        birthdays = {generate_birthday() for _ in range(50)}
        assert len(birthdays) > 1  # ランダム性の確認


class TestGenerateInitialNeuroState:
    def test_全パラメータが0から100内(self):
        for personality in ("tsundere", "amaenbo", "maipace"):
            state = generate_initial_neuro_state(personality, "03-15", rng_seed=42)
            for key in ("D", "S", "C", "O", "G", "E", "corruption"):
                assert 0.0 <= state[key] <= 100.0, f"{key}={state[key]}"

    def test_corruptionは常に0(self):
        state = generate_initial_neuro_state("tsundere", "01-01", rng_seed=1)
        assert state["corruption"] == 0.0

    def test_同じシードで同じ結果(self):
        s1 = generate_initial_neuro_state("maipace", "06-15", rng_seed=100)
        s2 = generate_initial_neuro_state("maipace", "06-15", rng_seed=100)
        assert s1 == s2

    def test_ツンデレはOが低め傾向(self):
        # シード固定で複数サンプル → ツンデレはOベースが低い
        tsundere_os = [
            generate_initial_neuro_state("tsundere", "99-99", rng_seed=i)["O"]
            for i in range(20)
        ]
        amaenbo_os = [
            generate_initial_neuro_state("amaenbo", "99-99", rng_seed=i)["O"]
            for i in range(20)
        ]
        avg_ts = sum(tsundere_os) / len(tsundere_os)
        avg_am = sum(amaenbo_os) / len(amaenbo_os)
        assert avg_ts < avg_am  # ツンデレのOは甘えん坊より低い


class TestCreateNewCat:
    def test_birthday形式が正しい(self):
        data = create_new_cat("maipace", rng_seed=42)
        parts = data.birthday.split("-")
        assert len(parts) == 2

    def test_neuro_stateに全キーが存在する(self):
        data = create_new_cat("tsundere", rng_seed=10)
        for key in ("D", "S", "C", "O", "G", "E", "corruption"):
            assert key in data.neuro_state
