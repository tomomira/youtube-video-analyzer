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
│   ├── youtube-api-setup-guide.md              # APIセットアップガイド
│   ├── installation-guide.md                   # インストールガイド
│   ├── user-manual.md                          # ユーザーマニュアル
│   └── build-guide.md                          # ビルドガイド
│
├── src/                        # ソースコード
│   ├── main.py                 # エントリーポイント
│   │
│   ├── ui/                     # UIレイヤー
│   │   ├── main_window.py      # メインウィンドウ
│   │   ├── search_panel.py     # 検索条件パネル
│   │   ├── result_panel.py     # 結果表示パネル
│   │   └── history_panel.py    # 検索履歴パネル
│   │
│   ├── application/            # アプリケーションレイヤー
│   │   ├── video_search_service.py    # 動画検索サービス
│   │   ├── preset_service.py          # プリセット管理サービス
│   │   └── history_service.py         # 検索履歴サービス
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
│   ├── test_models.py
│   └── test_integration.py
│
├── logs/                       # ログファイル（.gitignore対象）
│   └── youtube_analyzer.log
│
├── venv/                       # 仮想環境（.gitignore対象）
│
├── test_youtube_api.py         # YouTube API動作確認スクリプト
├── test_logger_usage.py        # ロガー使用例
├── test_core_functionality.py  # コア機能動作確認（GUIなし）
├── validate_build_config.py    # ビルド設定検証スクリプト
│
├── youtube_analyzer.spec       # PyInstallerビルド設定
├── build.bat                   # Windowsビルドスクリプト
├── build.sh                    # macOS/Linuxビルドスクリプト
│
├── .env                        # 環境変数（.gitignore対象）
├── .env.example                # 環境変数テンプレート
├── .gitignore                  # Git除外設定
├── requirements.txt            # 依存パッケージ
├── requirements-dev.txt        # 開発用パッケージ
├── README.md                   # プロジェクトREADME
├── RELEASE_NOTES.md            # リリースノート
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

### Phase 0: 環境構築・準備 ✅ 完了 (2025-11-24)
- 仮想環境構築
- YouTube APIキー取得
- 環境変数設定
- API動作確認
- ロギング実装

### Phase 1: コア機能実装 ✅ 完了 (2025-11-24)
- データモデル実装（VideoInfo, SearchCriteria, VideoType）
- YouTube APIクライアント実装
- 動画検索サービス実装
- ユニットテスト作成（53テスト）

### Phase 2: UI実装 ✅ 完了 (2025-11-25)
- Tkinterメインウィンドウ
- 検索条件入力フォーム
- 結果表示テーブル
- マルチスレッド対応

### Phase 3: エクスポート・拡張機能 ✅ 完了 (2025-11-25)
- Excel出力機能（openpyxl）
- Google Sheets連携（gspread）
- プリセット保存機能
- 検索履歴機能
- SQLiteデータベース実装

### Phase 4: UI拡張・統合テスト ✅ 完了 (2025-11-26)
- プリセット管理UI
- 検索履歴パネル（別ウィンドウ）
- Google Sheetsエクスポートメニュー
- 統合テスト（12テスト）
- バグ修正

### Phase 5: リリース準備 ✅ 完了 (2025-11-27)
- ユーザー向けドキュメント作成
  - インストールガイド
  - ユーザーマニュアル
  - ビルドガイド
- PyInstallerビルド設定
- リリースノート作成
- README更新

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

# コア機能動作確認（GUIなし）
python test_core_functionality.py

# ビルド設定検証
python validate_build_config.py
```

### ビルド（実行可能ファイル作成）

```bash
# Windows
build.bat

# macOS/Linux
bash build.sh

# または直接PyInstallerを実行
pyinstaller youtube_analyzer.spec
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

### 開発環境関連

#### tkinterが見つからない（WSL/Linux）
**問題**: `ModuleNotFoundError: No module named 'tkinter'`
**解決策**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/CentOS
sudo dnf install python3-tkinter
```

#### 日本語フォントが表示されない（WSL/Linux）
**問題**: GUIで日本語が□□□（豆腐）として表示される
**解決策**:
```bash
# Ubuntu/Debian
sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra

# Fedora/CentOS
sudo dnf install google-noto-sans-cjk-jp-fonts
```

#### WSLとWindows間で仮想環境が共有できない
**問題**: WSL環境で作成したvenvがWindows側で動作しない
**解決策**:
- WSL環境: `venv/bin/activate`
- Windows環境: `venv\Scripts\activate`
- それぞれの環境で別々の仮想環境を作成してください

詳細: `docs/installation-guide.md` のトラブルシューティングセクション参照

### YouTube API関連

**問題**: API呼び出しで403エラー
**解決策**:
1. APIキーが正しく設定されているか確認（`.env`ファイル）
2. YouTube Data API v3が有効化されているか確認
3. APIクォータが残っているか確認

**参考**: `docs/youtube-api-setup-guide.md`

**問題**: 検索結果が0件（フィルタリングが原因）
**解決策**:
- 最小再生回数/最大再生回数を空欄にしてみる
- ログで「検索結果: X件の動画IDを取得」→「フィルタリング後: 0件」となっている場合、フィルタが厳しすぎる
- 最小再生回数は「以上」、最大再生回数は「以下」を意味する

### エクスポート機能関連

**問題**: `TypeError: Excel does not support timezones in datetimes`
**解決策**:
- この問題は `src/infrastructure/excel_exporter.py` line 153 で修正済み
- 古いバージョンを使用している場合は最新版に更新してください

**問題**: Google Sheetsエクスポートできない
**解決策**:
```bash
# ライブラリをインストール
pip install gspread google-auth

# 認証情報を設定
# 1. Google Cloud Consoleでサービスアカウントを作成
# 2. JSONキーをダウンロード
# 3. .envに GOOGLE_CREDENTIALS_PATH=credentials.json を追加
```

### UI/UX関連

**問題**: WSLで日本語IME入力ができない
**解決策**:
1. コピー&ペーストを使用（推奨）
2. Windows環境で実行
3. fcitx-mozcをインストール（上級者向け）

**問題**: プリセットが読み込めない
**解決策**:
- プリセットドロップダウンから選択後に「読込」ボタンをクリック
- プリセットは検索条件を保存するもので、結果は保存されない
- 読み込み後に再度「検索」ボタンをクリックする必要がある

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

### 詳細なトラブルシューティング

上記以外の詳細なトラブルシューティング情報は以下を参照してください：
- [インストールガイド - トラブルシューティング](./docs/installation-guide.md#トラブルシューティング)
- [ユーザーマニュアル - よくある質問](./docs/user-manual.md#よくある質問)

## 参考資料

### プロジェクトドキュメント

#### ユーザー向け
- [README](./README.md) - プロジェクト概要
- [インストールガイド](./docs/installation-guide.md) - インストール方法
- [ユーザーマニュアル](./docs/user-manual.md) - 使い方
- [YouTube API セットアップガイド](./docs/youtube-api-setup-guide.md) - API設定

#### 開発者向け
- [要件定義書](./research/youtube-video-analyzer-requirements.md)
- [実装計画書](./research/implementation-plan.md)
- [ビルドガイド](./docs/build-guide.md) - 実行可能ファイルのビルド方法
- [Phase 0完了報告](./research/phase0-completion-report.md)
- [Phase 1完了報告](./research/phase1-completion-report.md)
- [Phase 2完了報告](./research/phase2-completion-report.md)
- [Phase 3完了報告](./research/phase3-completion-report.md)
- [Phase 4完了報告](./research/phase4-completion-report.md)
- [Phase 5完了報告](./research/phase5-completion-report.md)

### 外部リンク
- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [openpyxl ドキュメント](https://openpyxl.readthedocs.io/)
- [gspread ドキュメント](https://docs.gspread.org/)

## 開発状況

**最終更新**: 2025年11月27日
**現在のバージョン**: v1.0.0
**開発ステータス**: ✅ Phase 5完了（全機能実装完了）

### テスト状況
- ユニットテスト: 53/53 合格 ✅
- 統合テスト: 12/12 合格 ✅
- カバレッジ: 85%以上 ✅

### 次のステップ
- スタンドアロン実行可能ファイルのビルドとテスト
- GitHubリリースページでの配布
- ユーザーフィードバックの収集

---

このファイルは、Claude Codeがプロジェクトを理解し、適切なコードを生成するためのコンテキストとして使用されます。プロジェクトの進行に応じて随時更新してください。
