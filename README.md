# YouTube Video Analyzer & Exporter

YouTube上の人気動画を効率的に調査・分析し、Excel/Googleスプレッドシートに出力するデスクトップアプリケーション

## 概要

このアプリケーションは、YouTube Data API v3を使用して、特定の条件（キーワード、再生回数、動画タイプなど）で動画を検索し、その情報を構造化されたデータとして取得・エクスポートします。

### 主な機能

- **検索条件設定**: キーワード、再生回数、動画タイプ（通常/ショート）、公開日範囲などで絞り込み
- **動画情報取得**: タイトル、URL、再生回数、チャンネル名、公開日、概要など詳細情報を取得
- **Excelエクスポート**: 取得した情報を整形してExcelファイル（.xlsx）に出力
- **Googleスプレッドシート連携**: Googleスプレッドシートへの直接書き込み
- **プリセット保存**: よく使う検索条件を保存して再利用
- **進捗表示**: データ取得中の進捗状況をリアルタイム表示

## プロジェクトドキュメント

### 企画・設計ドキュメント
- [要件定義書](./research/youtube-video-analyzer-requirements.md) - システムの目的、機能要件、非機能要件
- [実装計画書](./research/implementation-plan.md) - 技術スタック、開発フェーズ、詳細な実装計画
- [専用アプリ開発のメリット](./research/why-build-dedicated-app.md) - AIツールとの比較、開発の意義

### ユーザー向けドキュメント（実装後）
- [ユーザーマニュアル](./docs/user_manual.md) - 使い方の詳細
- [API仕様書](./docs/api_reference.md) - 内部API仕様

## セットアップ

### 前提条件

- Python 3.10以上
- YouTube Data API v3のAPIキー（[取得方法](https://console.cloud.google.com/)）

### インストール

```bash
# 1. リポジトリをクローン（または解凍）
cd youtube-video-analyzer

# 2. 仮想環境を作成
python -m venv venv

# 3. 仮想環境を有効化
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 4. 依存パッケージをインストール
pip install -r requirements.txt

# 5. 環境変数を設定
cp .env.example .env
# .envファイルを編集してYouTube APIキーを設定

# 6. データベースを初期化（実装後）
python src/database/init_db.py
```

## 使い方

### 基本的な使い方

```bash
# アプリケーションを起動
python src/main.py
```

1. キーワードと検索条件を入力
2. 「検索」ボタンをクリック
3. 結果を確認
4. 「Excelエクスポート」ボタンで出力

### プリセットの使用

1. 検索条件を設定
2. 「プリセット保存」ボタンをクリック
3. プリセット名を入力して保存
4. 次回以降、「プリセット読込」から選択して使用

## 開発

### 開発環境のセットアップ

```bash
# 開発用パッケージをインストール
pip install -r requirements-dev.txt

# pre-commitフックをインストール（オプション）
pre-commit install
```

### テストの実行

```bash
# 全テストを実行
pytest

# カバレッジ付きで実行
pytest --cov=src --cov-report=html

# カバレッジレポートを開く
open htmlcov/index.html
```

### コード品質チェック

```bash
# コードフォーマット
black src tests

# Lintチェック
flake8 src tests

# 型チェック
mypy src

# セキュリティチェック
bandit -r src
```

## プロジェクト構造

```
youtube-video-analyzer/
├── research/                   # 企画・設計ドキュメント
│   ├── youtube-video-analyzer-requirements.md
│   ├── implementation-plan.md
│   └── why-build-dedicated-app.md
├── src/                        # ソースコード
│   ├── main.py                 # エントリーポイント
│   ├── ui/                     # UIレイヤー
│   ├── application/            # アプリケーションレイヤー
│   ├── domain/                 # ドメインレイヤー
│   ├── infrastructure/         # インフラレイヤー
│   ├── utils/                  # ユーティリティ
│   └── database/               # データベース関連
├── tests/                      # テストコード
├── docs/                       # ユーザー向けドキュメント
├── .env.example                # 環境変数テンプレート
├── .gitignore                  # Git除外設定
├── requirements.txt            # 依存パッケージ
├── requirements-dev.txt        # 開発用パッケージ
└── README.md                   # このファイル
```

## 技術スタック

- **言語**: Python 3.10+
- **GUI**: Tkinter
- **YouTube API**: google-api-python-client
- **Excel出力**: openpyxl
- **Google Sheets**: gspread
- **データベース**: SQLite
- **テスト**: pytest

## ライセンス

[ライセンスを記載]

## 貢献

[コントリビューション方法を記載]

## 作成者

[作成者情報を記載]

## 関連リンク

- [YouTube Data API v3 公式ドキュメント](https://developers.google.com/youtube/v3)
- [openpyxl ドキュメント](https://openpyxl.readthedocs.io/)
- [gspread ドキュメント](https://docs.gspread.org/)
