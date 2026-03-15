# ネコスイ 🐱

> **気分屋な猫と、距離感を育てるゲーム。**

猫吸いしたら吸わせてくれる時もあれば、足蹴りされる時もある。
仕組みはプレイヤーに見えない。「本当に気分屋だ」ってなる。

---

## ⚠️ 現在ベータ版です（無料公開中）

画像・音声はまだプレースホルダーです。
コア機能（猫AIの行動ロジック・LLM会話）は動作します。

> **将来的には有料版（立ち絵・音声・Electron版など）のリリースを予定しています。**
> ベータ期間中はすべての機能を無料でお試しいただけます。
> フィードバック・スターが開発の励みになります 🙏

---

## スクリーンショット

*(準備中)*

---

## 特徴

- **NeuroStateによる行動モデル** — 単純な好感度+1/-1ではなく、6種類の内部状態が複雑に絡み合う
- **同じ行動でも毎回違う反応** — 昨日は吸わせてくれたのに今日は逃げる
- **長期プレイで関係性が育つ** — 継続するほど猫の反応が変わっていく
- **仕組みが見えない** — だから本当に気分屋に感じる

---

## 動かし方

### 必要なもの

- Python 3.11+
- Node.js 20+
- [neurostate-engine](https://github.com/kagioneko/neurostate-engine)（別途クローン）

### セットアップ

```bash
# neurostate-engine を隣のディレクトリにクローン
git clone https://github.com/kagioneko/neurostate-engine ../neurostate-engine

# バックエンド
cd backend
pip install -r requirements.txt
cp .env.example .env
# .env に ANTHROPIC_API_KEY を入力（未設定でもテンプレートセリフで動作）
uvicorn main:app --reload --port 8000

# フロントエンド（別ターミナル）
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:5173` を開く。

---

## ロードマップ

| フェーズ | 内容 | 状態 |
|---------|------|------|
| **β** | バックエンドコア + React UI + MCPサーバー | ✅ 公開中 |
| **v0.5** | 立ち絵イラスト追加（6ポーズ × 3表情） | 🎨 制作中 |
| **v0.6** | BGM・SE追加、時間帯背景 | 📋 計画中 |
| **v1.0** | 毛色・性格5種、記憶エンジン統合、**スマホ対応（PWA）**、有料版リリース | 📋 計画中 |
| **v1.5** | Electron版（完全オフライン・APIキー自分持ち） | 📋 計画中 |
| **v2.0** | NovelAI連携でリアルタイム立ち絵生成 | 💡 構想中 |

### 💰 有料版について

v1.0以降で、オリジナル立ち絵・音声・追加コンテンツを含む有料版のリリースを検討しています。
コアのAIエンジン部分はオープンソースとして継続公開予定です。

---

## MCP サーバー（Claude Desktop / ChatGPT 連携）

ネコスイは **MCP（Model Context Protocol）サーバー**を同梱しています。
Claude Desktop や ChatGPT（MCP対応版）に追加すると、AIと会話しながら猫と遊べます。

### できること

- 「今の猫の気分で画像出して」→ AIが猫のNeuroStateを取得してDALL-Eなどで絵を描く
- 「猫吸いして」→ AIがアクションを実行して猫の反応を返す
- 「ミルの今の状態は？」→ 親密度・NeuroState・時間帯をまとめて返す

### セットアップ

```bash
# 依存パッケージ（バックエンドと共通）
cd backend
pip install -r requirements.txt
```

### Claude Desktop に追加する

`~/Library/Application Support/Claude/claude_desktop_config.json`（Mac）または
`%APPDATA%\Claude\claude_desktop_config.json`（Windows）に追記：

```json
{
  "mcpServers": {
    "nekosui": {
      "command": "python3",
      "args": ["/path/to/nekosui/mcp_server.py"]
    }
  }
}
```

`/path/to/nekosui/` をクローンしたディレクトリの実際のパスに変えてください。

### ChatGPT に追加する

ChatGPT の設定 → **Connectors** → **Add MCP Server** から `mcp_config.json` の内容を参考に追加してください。

### ツール一覧

| ツール | 説明 |
|--------|------|
| `get_cat_status` | 猫の現在のNeuroState・気分・親密度を取得 |
| `do_action` | 猫にアクション（猫吸い・なでる・ごはんなど） |
| `setup_cat` | 新しい猫を作る（名前・性格・毛色を指定） |

---

## 技術スタック

- **フロントエンド**: React + TypeScript + Vite + TailwindCSS
- **バックエンド**: FastAPI + SQLite + aiosqlite
- **MCP サーバー**: [MCP Python SDK](https://github.com/anthropics/mcp)
- **AI**: [neurostate-engine](https://github.com/kagioneko/neurostate-engine) + Claude Haiku (Anthropic)

---

## ライセンス

MIT License

---

## 作者

**Emilia Lab** / Aya Mizutani
[GitHub](https://github.com/emilialab) · [kagioneko.com](https://kagioneko.com/emilia_lab/)
