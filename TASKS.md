# ネコスイ — タスク一覧

## Phase 0: 準備

- [ ] 立ち絵イラスト発注 or 生成（6ポーズ × 3表情 = 18枚、まず1毛色分）
- [ ] プロジェクトリポジトリ作成
- [ ] 開発環境セットアップ（Vite + FastAPI）

## Phase 1: バックエンドコア（LLMなし・動作確認用）

> **MVP方針: まずノベルゲーム形式で完成させる。画像生成・Live2Dは後回し。**



- [ ] 初期NeuroStateランダム化（`cat_initializer.py`）
  - [ ] 性格プリセット別の揺らぎ幅定義（ツンデレ大・マイペース小）
  - [ ] gaussian randomで初期値生成（clamp 0-100）
  - [ ] 誕生日ランダム設定（誕生日当日D・E爆上がり）
  - [ ] 曜日による微揺らぎ（月曜S低め・金曜D高め）
- [ ] DBスキーマ設計・作成（SQLite: cats / sessions / chat_history）
- [ ] Pydanticスキーマ定義
- [ ] 時間帯判定ロジック（`time_behavior.py`）
- [ ] アクション → NeuroStateイベント変換（`cat_event_mapper.py`）
  - [ ] 猫吸い（連続回数チェック・逃げる判定含む）
  - [ ] なでる / ごはん / 遊ぶ / 抱っこ / 名前を呼ぶ / 無視
- [ ] NeuroState → 猫の行動決定（`cat_behavior.py`）
  - [ ] 返事するか判定
  - [ ] 返事の長さ・口調
  - [ ] 立ち絵キー（ポーズ + 表情）の選択
  - [ ] 逃げる判定・帰宅判定
- [ ] セッション管理（`session_manager.py`）
- [ ] FastAPIエンドポイント
  - [ ] POST /api/cat/setup
  - [ ] GET  /api/cat/status/{session_id}
  - [ ] POST /api/chat
  - [ ] POST /api/cat/reset/{session_id}
  - [ ] GET  /api/health
- [ ] ユニットテスト（cat_behavior / cat_event_mapper / time_behavior）

## Phase 2: LLM + 性格システム

- [ ] 猫用BiasEngineプリセット定義（ツンデレ / 甘えん坊 / マイペース）
- [ ] 猫用system promptビルダー（`cat_prompt_builder.py`）
  - [ ] NeuroState値 → 口調ガイドライン変換
  - [ ] 時間帯・性格・親密度を反映
  - [ ] 猫語・語尾ルール
- [ ] LLMクライアント（`llm_client.py`）
  - [ ] Claude Haiku対応
  - [ ] OpenAI対応
  - [ ] Ollama対応（デスクトップ版用）
  - [ ] フォールバック（LLM不要時は固定返事）
- [ ] chatエンドポイントにLLM統合
- [ ] 統合テスト

## Phase 3: フロントエンド（ネット版）

- [ ] Vite + React + TailwindCSSセットアップ
- [ ] 型定義・APIクライアント
- [ ] SetupScreen（名前 / 性格 / 毛色選択）
- [ ] ChatScreen（メイン画面）
  - [ ] 立ち絵表示（ポーズ+表情切替・fadeトランジション）
  - [ ] 逃げる演出（スライドアウト → 「どこかへ行ってしまった…」）
  - [ ] チャットバブル（猫: 左 / ユーザー: 右）
  - [ ] アクションバー（猫吸い / なでる / ごはん / 遊ぶ / 抱っこ / 名前を呼ぶ）
  - [ ] テキスト入力
- [ ] 時間帯背景グラデーション（朝/昼/夕/夜/深夜）
- [ ] TimeIndicator（時間帯アイコン表示）
- [ ] 親密度メーター（ハートゲージ）
- [ ] NeuroStateデバッグパネル（任意表示）

## Phase 4: 記憶・関係性

- [ ] memory-engine-mcp統合（`relationship_manager.py`）
- [ ] セッション終了時の自動要約（猫の主観日記）
- [ ] system promptに記憶埋め込み
- [ ] ユーザー行動時間の記録（何時に来るか）

## Phase 5: デスクトップ版

- [ ] Electron化
- [ ] 設定画面（APIキー入力: OpenAI / Anthropic / Gemini / Ollama URL）
- [ ] 接続テスト機能
- [ ] 完全オフライン動作確認
- [ ] セーブデータエクスポート/インポート（ネット版との引き継ぎ）

## Phase 6: ユーザー行動学習（v1.5）

- [ ] 来訪時間帯ログの集計
- [ ] ユーザーごとの時間帯補正値を動的に変化させる
- [ ] 「夜型の猫になる」「昼でも起きてる猫になる」実装

## Phase 7: 立ち絵拡張（v1.5〜）

- [ ] 残り毛色分の立ち絵追加（5色 × 18枚）
- [ ] Live2D対応（live2d-cubism-sdk-web）
- [ ] アクション時の簡易アニメーション

## Phase 8: 生成AI連携（v2.0〜）

- [ ] NeuroState → 画像生成プロンプト変換
- [ ] NovelAI API / SD WebUI API接続
- [ ] アクション時だけ生成（コスト抑制）
- [ ] 生成画像キャッシュ

## 未分類・検討中

- [ ] BGM（時間帯で変化・環境音）
- [ ] 通知機能（「ミルがごはんを要求しています」）
- [ ] スマホ版（React Native? / PWA?）
- [ ] チャッピーへの共有・レビュー依頼

---

## 優先度まとめ

```
今すぐ: Phase 0（立ち絵）+ Phase 1（バックエンドコア）
次:     Phase 2（LLM）+ Phase 3（フロントエンド）
後で:   Phase 4以降
```
