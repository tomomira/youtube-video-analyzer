# YouTube Video Analyzer & Exporter

YouTube上の人気動画を効率的に調査・分析し、Excel/Googleスプレッドシートに出力するデスクトップアプリケーション

## プロジェクト概要

このプロジェクトは、YouTube Data API v3を使用して、特定の検索条件（キーワード、再生回数、動画タイプなど）で動画を検索し、その情報を構造化されたデータとして取得・エクスポートするPythonデスクトップアプリケーションです。

### 主な機能

- 検索条件設定（キーワード、再生回数、動画タイプ、公開日範囲）
- YouTube動画情報の取得（タイトル、URL、再生回数、チャンネル名、概要等）
- Excelファイル（.xlsx）への出力
- Googleスプレッドシートへの直接書き込み
- 検索条件プリセットの保存・読込機能
- ショート動画の自動識別（60秒以下）

## 技術スタック

### 言語・フレームワーク
- **Python**: 3.10以上
- **GUI**: Tkinter（標準ライブラリ）

### 主要ライブラリ
- **google-api-python-client**: YouTube Data API v3クライアント
- **openpyxl**: Excel(.xlsx)ファイル生成
- **gspread**: Google Sheets API連携
- **python-dotenv**: 環境変数管理
- **isodate**: ISO 8601形式の期間パース
- **pytest**: テストフレームワーク

### データベース
- **SQLite**: プリセット・検索履歴の保存

## アーキテクチャ

### レイヤー構造

プロジェクトはレイヤードアーキテクチャを採用しています：

```
UI Layer (src/ui/)
    ↓
Application Layer (src/application/)
    ↓
Domain Layer (src/domain/)
    ↓
Infrastructure Layer (src/infrastructure/)
```

### ディレクトリ構造

```
youtube-video-analyzer/
├── research/                   # 企画・設計ドキュメント
│   ├── youtube-video-analyzer-requirements.md  # 要件定義書
│   ├── implementation-plan.md                  # 実装計画書
│   ├── why-build-dedicated-app.md              # 開発の意義
│   └── phase0-completion-report.md             # Phase 0完了報告
│
├── docs/                       # ユーザー向けドキュメント
│   └── youtube-api-setup-guide.md              # APIセットアップガイド
│
├── src/                        # ソースコード
│   ├── main.py                 # エントリーポイント
│   │
│   ├── ui/                     # UIレイヤー
│   │   ├── main_window.py      # メインウィンドウ
│   │   ├── search_panel.py     # 検索条件パネル
│   │   └── result_panel.py     # 結果表示パネル
│   │
│   ├── application/            # アプリケーションレイヤー
│   │   ├── video_search_service.py    # 動画検索サービス
│   │   ├── export_service.py          # エクスポートサービス
│   │   └── preset_service.py          # プリセット管理サービス
│   │
│   ├── domain/                 # ドメインレイヤー
│   │   ├── models.py           # データモデル（VideoInfo, SearchCriteria等）
│   │   └── value_objects.py    # 値オブジェクト
│   │
│   ├── infrastructure/         # インフラレイヤー
│   │   ├── youtube_client.py   # YouTube APIクライアント
│   │   ├── excel_exporter.py   # Excel出力
│   │   ├── sheets_exporter.py  # Google Sheets出力
│   │   └── database.py         # SQLiteアクセス
│   │
│   ├── utils/                  # ユーティリティ
│   │   └── logger.py           # ロギング設定
│   │
│   └── database/               # データベース関連
│       └── init_db.py          # DB初期化スクリプト
│
├── tests/                      # テストコード
│   ├── test_youtube_client.py
│   ├── test_video_search_service.py
│   └── test_export_service.py
│
├── logs/                       # ログファイル（.gitignore対象）
│   └── youtube_analyzer.log
│
├── venv/                       # 仮想環境（.gitignore対象）
│
├── test_youtube_api.py         # YouTube API動作確認スクリプト
├── test_logger_usage.py        # ロガー使用例
│
├── .env                        # 環境変数（.gitignore対象）
├── .env.example                # 環境変数テンプレート
├── .gitignore                  # Git除外設定
├── requirements.txt            # 依存パッケージ
├── requirements-dev.txt        # 開発用パッケージ
├── README.md                   # プロジェクトREADME
└── CLAUDE.MD                   # このファイル
```

## 重要な実装詳細

### 1. ショート動画の識別方法

YouTube APIにはショート動画専用のフラグが存在しないため、以下の方法で識別します：

```python
import isodate

# videos.list APIで contentDetails.duration を取得（ISO 8601形式）
duration_str = video['contentDetails']['duration']  # 例: "PT42S" or "PT4H26M52S"

# 秒数に変換
duration_seconds = int(isodate.parse_duration(duration_str).total_seconds())

# 60秒以下をショート動画と判定
is_short = duration_seconds <= 60
```

**参考**: `test_youtube_api.py` で動作確認済み

### 2. ロギングの使用方法

プロジェクト全体で統一されたロギングを使用します：

```python
from src.utils.logger import get_logger

# モジュール固有のロガーを取得
logger = get_logger(__name__)

# ログ出力
logger.info("処理を開始しました")
logger.warning("APIクォータ残量が少なくなっています")
logger.error("エラーが発生しました", exc_info=True)  # スタックトレース付き
```

**ログ出力先**:
- コンソール（標準出力）
- ファイル（`logs/youtube_analyzer.log`）

**ログレベル設定**: `.env`ファイルの`LOG_LEVEL`で変更可能（DEBUG, INFO, WARNING, ERROR, CRITICAL）

### 3. 環境変数

`.env`ファイルで管理（`.env.example`をコピーして作成）：

```bash
# YouTube Data API v3
YOUTUBE_API_KEY=your_api_key_here

# Google Sheets API（オプション）
GOOGLE_CREDENTIALS_PATH=credentials.json

# アプリケーション設定
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=500
DATABASE_PATH=youtube_analyzer.db
```

### 4. YouTube API制限

- **デフォルトクォータ**: 10,000ユニット/日
- **search.list**: 100ユニット/リクエスト
- **videos.list**: 1ユニット/リクエスト

**重要**: 過度な検索を避けるため、`MAX_SEARCH_RESULTS`で上限を設定

## 開発フェーズ

### Phase 0: 環境構築・準備 ✅ 完了
- 仮想環境構築
- YouTube APIキー取得
- 環境変数設定
- API動作確認
- ロギング実装

### Phase 1: コア機能実装（現在）
- データモデル実装
- YouTube APIクライアント実装
- 検索サービス実装
- ユニットテスト作成

### Phase 2: UI実装
- Tkinterメインウィンドウ
- 検索条件入力フォーム
- 結果表示テーブル
- 進捗表示

### Phase 3: エクスポート・拡張機能
- Excel出力機能
- Google Sheets連携
- プリセット保存機能
- 検索履歴機能

### Phase 4: テスト・デバッグ
- 統合テスト
- パフォーマンステスト
- バグ修正

### Phase 5: リリース準備
- ドキュメント整備
- インストーラー作成
- デプロイ準備

## よく使うコマンド

### 仮想環境の有効化

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### アプリケーション起動（Phase 2以降）

```bash
python src/main.py
```

### テスト実行

```bash
# 全テストを実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定のテストファイルのみ
pytest tests/test_youtube_client.py
```

### コード品質チェック

```bash
# フォーマット
black src tests

# Lint
flake8 src tests

# 型チェック
mypy src

# セキュリティチェック
bandit -r src
```

### 動作確認スクリプト

```bash
# YouTube API動作確認
python test_youtube_api.py

# ロガー動作確認
python test_logger_usage.py
```

## コーディング規約

### 1. インポート順序

```python
# 1. 標準ライブラリ
import os
import sys
from typing import List, Dict

# 2. サードパーティライブラリ
from googleapiclient.discovery import build
import openpyxl

# 3. ローカルモジュール
from src.utils.logger import get_logger
from src.domain.models import VideoInfo
```

### 2. 命名規則

- **クラス**: PascalCase（例: `VideoSearchService`）
- **関数・変数**: snake_case（例: `get_video_details`）
- **定数**: UPPER_SNAKE_CASE（例: `MAX_RESULTS`）
- **プライベート**: 先頭にアンダースコア（例: `_internal_method`）

### 3. 型ヒント

必ず型ヒントを使用する：

```python
def search_videos(keyword: str, max_results: int = 50) -> List[VideoInfo]:
    """動画を検索する"""
    pass
```

### 4. Docstring

Google styleで記述：

```python
def get_video_details(video_id: str) -> VideoInfo:
    """
    動画の詳細情報を取得する

    Args:
        video_id: YouTube動画ID

    Returns:
        VideoInfo: 動画情報オブジェクト

    Raises:
        APIError: API呼び出しに失敗した場合
    """
    pass
```

### 5. エラーハンドリング

必ずロギングと共にエラーを記録：

```python
try:
    result = api_call()
except HttpError as e:
    logger.error(f"API呼び出しエラー: {e}", exc_info=True)
    raise
```

## トラブルシューティング

### YouTube API関連

**問題**: API呼び出しで403エラー
**解決策**:
1. APIキーが正しく設定されているか確認（`.env`ファイル）
2. YouTube Data API v3が有効化されているか確認
3. APIクォータが残っているか確認

**参考**: `docs/youtube-api-setup-guide.md`

### 依存パッケージ関連

**問題**: `ModuleNotFoundError`
**解決策**:
```bash
source venv/bin/activate  # 仮想環境を有効化
pip install -r requirements.txt
```

### ログファイルが作成されない

**問題**: `logs/youtube_analyzer.log`が生成されない
**解決策**:
```bash
mkdir -p logs  # logsディレクトリを作成
python src/utils/logger.py  # ロガーをテスト実行
```

## 参考資料

### プロジェクトドキュメント
- [要件定義書](./research/youtube-video-analyzer-requirements.md)
- [実装計画書](./research/implementation-plan.md)
- [Phase 0完了報告](./research/phase0-completion-report.md)
- [YouTube API セットアップガイド](./docs/youtube-api-setup-guide.md)

### 外部リンク
- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [openpyxl ドキュメント](https://openpyxl.readthedocs.io/)
- [gspread ドキュメント](https://docs.gspread.org/)

## 開発状況

**最終更新**: 2025年11月24日
**現在のフェーズ**: Phase 1（コア機能実装）
**次のタスク**: データモデルの実装（`src/domain/models.py`）

---

このファイルは、Claude Codeがプロジェクトを理解し、適切なコードを生成するためのコンテキストとして使用されます。プロジェクトの進行に応じて随時更新してください。
