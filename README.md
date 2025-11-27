# YouTube Video Analyzer

<p align="center">
  <strong>YouTube動画を効率的に検索・分析し、Excel/Google Spreadsheetsにエクスポートするデスクトップアプリケーション</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

---

## 📋 概要

YouTube Video Analyzerは、YouTube Data API v3を使用して、キーワードや再生回数などの条件で動画を検索し、結果をExcelファイルやGoogle Spreadsheetsにエクスポートできるデスクトップアプリケーションです。

### ✨ 主な機能

- 🔍 **高度な検索**: キーワード、再生回数、動画タイプ（通常/ショート）で絞り込み
- 📊 **見やすい結果表示**: テーブル形式で表示、列ごとにソート可能
- 📁 **Excelエクスポート**: 整形された.xlsxファイルに出力
- ☁️ **Google Sheets連携**: クラウド上のスプレッドシートに直接書き込み
- 💾 **プリセット機能**: よく使う検索条件を保存して再利用
- 📜 **検索履歴**: 過去の検索を確認・再実行
- 🎯 **ショート動画判定**: 60秒以下の動画を自動識別

---

## 🖼️ スクリーンショット

```
┌─────────────────────────────────────────────────────────┐
│ YouTube Video Analyzer                                  │
├─────────────────────────────────────────────────────────┤
│ プリセット: [Python動画検索] [読込][保存][削除]         │
│ 検索キーワード: [Python tutorial___________________]    │
│ 最小再生回数: [10000] 最大再生回数: [_______]           │
│ 動画タイプ: ◉すべて ○ショート ○通常                   │
│ 最大取得件数: [50] ソート順: [viewCount▼]              │
│                      [検索]                              │
├─────────────────────────────────────────────────────────┤
│ 検索結果: 42件           [Excelにエクスポート]          │
│┌───────────────────────────────────────────────────────┐│
││タイトル         │チャンネル  │再生回数│長さ │公開日││
││Python Tutorial  │Code Academy│1.2M    │15:32│2024...││
││Learn Python...  │Tech Channel│850K    │22:15│2024...││
│└───────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 クイックスタート

### システム要件

- **Python**: 3.10以上
- **OS**: Windows 10/11, macOS 10.14+, Linux（Ubuntu 20.04+）
- **インターネット接続**: YouTube API利用に必要

### インストール

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-repo/youtube-video-analyzer.git
cd youtube-video-analyzer

# 2. 仮想環境を作成して有効化
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 環境変数を設定
cp .env.example .env
# .envファイルを編集してYouTube APIキーを設定
```

### YouTube APIキーの取得

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. 「YouTube Data API v3」を有効化
4. APIキーを作成
5. `.env`ファイルに設定

**詳しい手順は [YouTube API セットアップガイド](./docs/youtube-api-setup-guide.md) を参照**

### 起動

```bash
python src/main.py
```

---

## 📖 ドキュメント

### ユーザー向け

- 📘 [インストールガイド](./docs/installation-guide.md) - 詳細なインストール手順
- 📙 [ユーザーマニュアル](./docs/user-manual.md) - 機能の使い方
- 📗 [YouTube API セットアップガイド](./docs/youtube-api-setup-guide.md) - API設定方法

### 開発者向け

- 📕 [CLAUDE.MD](./CLAUDE.MD) - プロジェクト全体の開発情報
- 📓 [実装計画書](./research/implementation-plan.md) - 技術スタック、開発フェーズ
- 📔 [Phase完了報告](./research/) - 各フェーズの詳細な実装内容

---

## 💡 使い方

### 基本的な検索

1. **検索キーワード**を入力（例: "Python tutorial"）
2. **検索条件**を設定（再生回数、動画タイプなど）
3. **検索**ボタンをクリック
4. 結果をテーブルで確認

### プリセットの活用

```
よく使う検索条件を保存:
1. 検索条件を入力
2. 「保存」ボタンをクリック
3. プリセット名を入力

次回の使用:
1. プリセットを選択
2. 「読込」ボタンをクリック
3. 「検索」ボタンをクリック
```

### エクスポート

- **Excel**: 「Excelにエクスポート」ボタン → 保存先を選択
- **Google Sheets**: メニューバー「ファイル」→「Google Sheetsにエクスポート」

### 検索履歴

メニューバー「表示」→「検索履歴」で過去の検索を確認・再実行

---

## 🛠️ 開発

### 開発環境のセットアップ

```bash
# 開発用パッケージをインストール
pip install -r requirements-dev.txt
```

### テストの実行

```bash
# 全テストを実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 統合テストのみ
pytest tests/test_integration.py -v
```

**テスト結果**: 12/12 テスト合格 ✅

### コード品質チェック

```bash
# フォーマット
black src tests

# Lint
flake8 src tests

# 型チェック
mypy src
```

---

## 📁 プロジェクト構造

```
youtube-video-analyzer/
├── src/                        # ソースコード
│   ├── main.py                 # エントリーポイント
│   ├── ui/                     # UIレイヤー
│   │   ├── main_window.py      # メインウィンドウ
│   │   ├── search_panel.py     # 検索パネル
│   │   ├── result_panel.py     # 結果表示
│   │   └── history_panel.py    # 検索履歴
│   ├── application/            # アプリケーションレイヤー
│   │   ├── video_search_service.py
│   │   ├── preset_service.py
│   │   └── history_service.py
│   ├── domain/                 # ドメインレイヤー
│   │   └── models.py           # データモデル
│   ├── infrastructure/         # インフラレイヤー
│   │   ├── youtube_client.py   # YouTube API
│   │   ├── excel_exporter.py   # Excel出力
│   │   └── sheets_exporter.py  # Google Sheets
│   ├── utils/                  # ユーティリティ
│   │   └── logger.py
│   └── database/               # データベース
│       └── init_db.py
├── tests/                      # テストコード
│   ├── test_models.py
│   ├── test_youtube_client.py
│   └── test_integration.py
├── docs/                       # ドキュメント
│   ├── installation-guide.md
│   ├── user-manual.md
│   └── youtube-api-setup-guide.md
├── research/                   # 設計ドキュメント
│   ├── phase0-completion-report.md
│   ├── phase1-completion-report.md
│   ├── phase2-completion-report.md
│   ├── phase3-completion-report.md
│   ├── phase4-completion-report.md
│   └── phase5-completion-report.md
├── .env.example                # 環境変数テンプレート
├── requirements.txt            # 依存パッケージ
├── requirements-dev.txt        # 開発用パッケージ
├── CLAUDE.MD                   # 開発者向けドキュメント
└── README.md                   # このファイル
```

---

## 🔧 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **言語** | Python 3.10+ |
| **GUI** | Tkinter (ttk) |
| **YouTube API** | google-api-python-client |
| **Excel出力** | openpyxl |
| **Google Sheets** | gspread, google-auth |
| **データベース** | SQLite3 |
| **テスト** | pytest, pytest-mock |
| **コード品質** | black, flake8, mypy |

---

## 🐛 トラブルシューティング

### よくある問題

#### Q: 「YouTube API キーが設定されていません」エラー

**A**: `.env`ファイルにAPIキーが正しく設定されているか確認してください。

```bash
# .env ファイルの内容を確認
cat .env

# 正しい形式
YOUTUBE_API_KEY=your_actual_api_key_here
```

#### Q: 検索結果が0件

**A**: 以下を確認：
1. APIクォータが残っているか（1日10,000ユニット）
2. 検索条件が厳しすぎないか
3. キーワードが適切か

#### Q: モジュールが見つからないエラー

**A**: 仮想環境を有効化して依存パッケージを再インストール

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**詳細は [インストールガイド](./docs/installation-guide.md#トラブルシューティング) を参照**

---

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

## 🤝 貢献

バグ報告や機能リクエストは [GitHub Issues](https://github.com/your-repo/issues) でお願いします。

プルリクエストも歓迎します！

---

## 👨‍💻 開発履歴

- **Phase 0** (2025-11): 環境構築・準備
- **Phase 1** (2025-11): コア機能実装
- **Phase 2** (2025-11): UI実装
- **Phase 3** (2025-11): エクスポート・拡張機能
- **Phase 4** (2025-11): UI拡張・統合テスト
- **Phase 5** (2025-11): リリース準備・ドキュメント整備

詳細は各Phase完了報告書（`research/`）を参照してください。

---

## 🔗 関連リンク

- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [openpyxl ドキュメント](https://openpyxl.readthedocs.io/)
- [gspread ドキュメント](https://docs.gspread.org/)

---

<p align="center">
  Made with ❤️ by Claude Code
</p>
