# YouTube Video Analyzer インストールガイド

## 目次

1. [システム要件](#システム要件)
2. [インストール方法](#インストール方法)
3. [初期設定](#初期設定)
4. [起動方法](#起動方法)
5. [トラブルシューティング](#トラブルシューティング)

---

## システム要件

### 必須要件

- **OS**: Windows 10/11, macOS 10.14以降, Linux（Ubuntu 20.04以降推奨）
- **メモリ**: 4GB以上推奨
- **ディスク空き容量**: 500MB以上
- **インターネット接続**: YouTube API利用に必要

### 推奨要件

- **Python**: 3.10以上（ソースコードから実行する場合）
- **メモリ**: 8GB以上
- **ディスク空き容量**: 1GB以上

---

## インストール方法

### 方法1: インストーラーを使う（推奨・初心者向け）

**注意**: 現在、インストーラー版は開発中です。以下の方法2をご利用ください。

将来的には以下の手順でインストール可能になります：

1. [リリースページ](https://github.com/your-repo/releases)から最新版をダウンロード
2. インストーラーを実行
3. インストール先を選択
4. デスクトップアイコンから起動

---

### 方法2: Pythonから実行する（現在の方法）

#### ステップ1: Pythonのインストール

**Windows**:
1. [Python公式サイト](https://www.python.org/downloads/)から最新版（3.10以上）をダウンロード
2. インストーラーを実行
3. **「Add Python to PATH」にチェックを入れる**（重要）
4. 「Install Now」をクリック

**macOS**:
```bash
# Homebrewを使用（推奨）
brew install python@3.10
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

#### ステップ2: プロジェクトのダウンロード

**方法A: GitHubからクローン**（推奨）
```bash
git clone https://github.com/your-repo/youtube-video-analyzer.git
cd youtube-video-analyzer
```

**方法B: ZIPファイルをダウンロード**
1. GitHubのリポジトリページで「Code」→「Download ZIP」
2. ZIPファイルを展開
3. ターミナル/コマンドプロンプトで展開したフォルダに移動

#### ステップ3: 仮想環境の作成

```bash
# 仮想環境を作成
python -m venv venv

# 仮想環境を有効化
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**仮想環境が有効化されると、プロンプトの先頭に `(venv)` が表示されます。**

#### ステップ4: 依存パッケージのインストール

```bash
# 必須パッケージをインストール
pip install -r requirements.txt

# 開発用パッケージもインストールする場合（オプション）
pip install -r requirements-dev.txt
```

**インストールには数分かかる場合があります。**

---

## 初期設定

### YouTube API キーの取得

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成
3. 「APIとサービス」→「ライブラリ」に移動
4. 「YouTube Data API v3」を検索して有効化
5. 「認証情報」→「認証情報を作成」→「APIキー」
6. 生成されたAPIキーをコピー

**詳細な手順は [YouTube API セットアップガイド](./youtube-api-setup-guide.md) を参照してください。**

### 環境変数の設定

1. プロジェクトのルートディレクトリに `.env` ファイルを作成
2. 以下の内容を記述（APIキーは先ほどコピーしたものを使用）

```bash
# YouTube Data API v3
YOUTUBE_API_KEY=your_api_key_here

# Google Sheets API（オプション、使わない場合は削除可）
# GOOGLE_CREDENTIALS_PATH=credentials.json

# アプリケーション設定
LOG_LEVEL=INFO
MAX_SEARCH_RESULTS=500
DATABASE_PATH=youtube_analyzer.db
```

**重要**: `.env` ファイルにはAPIキーなどの機密情報が含まれます。他人と共有しないでください。

### .env.example ファイルの利用

プロジェクトには `.env.example` というテンプレートファイルが含まれています：

```bash
# テンプレートをコピー
cp .env.example .env

# エディタで開いてAPIキーを設定
nano .env  # または vi, vim, code など
```

---

## 起動方法

### コマンドラインから起動

```bash
# 仮想環境を有効化（まだの場合）
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# アプリケーションを起動
python src/main.py
```

### 起動後の画面

正常に起動すると、以下のようなGUIウィンドウが表示されます：

```
┌─────────────────────────────────────────┐
│ YouTube Video Analyzer                  │
├─────────────────────────────────────────┤
│ プリセット: [選択...] [読込][保存][削除]│
│ 検索キーワード: [____________]          │
│ 最小再生回数: [______]                  │
│ ...                                     │
│ [検索]                                  │
├─────────────────────────────────────────┤
│ 検索結果: 0件                           │
│ ┌──────────────────────────────────┐    │
│ │タイトル│チャンネル│再生回数│...│    │
│ └──────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## トラブルシューティング

### よくある問題

#### 1. 「YouTube API キーが設定されていません」エラー

**症状**: アプリ起動時にエラーダイアログが表示される

**解決方法**:
- `.env` ファイルが正しく作成されているか確認
- `YOUTUBE_API_KEY=` の後にAPIキーが正しく入力されているか確認
- `.env` ファイルがプロジェクトのルートディレクトリにあるか確認

#### 2. 「ModuleNotFoundError」エラー

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解決方法**:
```bash
# 仮想環境が有効化されているか確認
# プロンプトの先頭に (venv) が表示されているか確認

# 依存パッケージを再インストール
pip install -r requirements.txt
```

#### 3. tkinterが見つからないエラー（Linux）

**症状**: `ModuleNotFoundError: No module named 'tkinter'`

**解決方法** (Ubuntu/Debian):
```bash
sudo apt-get install python3-tk
```

**解決方法** (Fedora/CentOS):
```bash
sudo dnf install python3-tkinter
```

#### 4. 検索結果が0件

**原因と解決方法**:

1. **APIクォータ超過**
   - YouTube Data API v3は1日10,000ユニットまで
   - 翌日まで待つ、または新しいプロジェクトを作成

2. **検索条件が厳しすぎる**
   - 再生回数の範囲を広げる
   - キーワードを変更する

3. **APIキーの制限**
   - Google Cloud Consoleで「APIキー」の制限を確認
   - YouTube Data API v3が許可されているか確認

#### 5. Excelエクスポートできない

**症状**: エクスポートボタンをクリックしてもファイルが作成されない

**解決方法**:
```bash
# openpyxlを再インストール
pip install --upgrade openpyxl
```

#### 6. Google Sheetsエクスポートできない

**症状**: 「Google Sheetsエクスポートに必要なライブラリがインストールされていません」

**解決方法**:
```bash
# gspreadと認証ライブラリをインストール
pip install gspread google-auth
```

**症状**: 「Google API認証情報が設定されていません」

**解決方法**:
1. Google Cloud Consoleでサービスアカウントを作成
2. JSONキーファイルをダウンロード
3. `.env` ファイルに `GOOGLE_CREDENTIALS_PATH=credentials.json` を追加

---

## アンインストール

### 方法2（Pythonから実行）でインストールした場合

```bash
# プロジェクトフォルダを削除するだけ
cd ..
rm -rf youtube-video-analyzer  # Linux/macOS
# または
rmdir /s youtube-video-analyzer  # Windows
```

**注意**: データベースファイル（`youtube_analyzer.db`）やログファイルも削除されます。

---

## サポート

### 問題が解決しない場合

1. [GitHub Issues](https://github.com/your-repo/issues)で既存の問題を検索
2. 該当する問題がない場合は、新しいIssueを作成
3. 以下の情報を含めてください：
   - OS名とバージョン
   - Pythonバージョン (`python --version`)
   - エラーメッセージの全文
   - 実行したコマンド

### ドキュメント

- [ユーザーマニュアル](./user-manual.md) - 詳しい使い方
- [YouTube API セットアップガイド](./youtube-api-setup-guide.md) - API設定の詳細
- [開発者向けドキュメント](../CLAUDE.MD) - 開発に関する情報

---

**最終更新**: 2025年11月26日
