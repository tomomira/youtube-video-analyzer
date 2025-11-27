# YouTube Video Analyzer ビルドガイド

このガイドでは、YouTube Video Analyzerをスタンドアロン実行可能ファイルとしてビルドする方法を説明します。

## 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [ビルド方法](#ビルド方法)
4. [配布方法](#配布方法)
5. [トラブルシューティング](#トラブルシューティング)

---

## 概要

### ビルドの目的

スタンドアロン実行可能ファイルを作成することで、以下のメリットがあります：

- **Pythonのインストール不要**: エンドユーザーはPythonをインストールする必要がありません
- **依存関係の簡略化**: すべてのライブラリが実行可能ファイルに含まれます
- **配布の容易さ**: 単一のフォルダをZIP圧縮して配布できます

### ビルドツール

**PyInstaller**を使用します。PyInstallerは、Pythonアプリケーションをスタンドアロン実行可能ファイルに変換するツールです。

---

## 前提条件

### 必須要件

- **Python**: 3.10以上
- **OS**: Windows 10/11, macOS 10.14以降, Linux（Ubuntu 20.04以降推奨）
- **仮想環境**: プロジェクトの仮想環境が作成済みであること

### ビルド前の確認

```bash
# 仮想環境を有効化
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 依存パッケージがインストールされているか確認
pip list | grep pyinstaller
# pyinstaller 6.2.0 が表示されればOK
```

**注意**: PyInstallerがインストールされていない場合：

```bash
pip install -r requirements-dev.txt
```

---

## ビルド方法

### 方法1: ビルドスクリプトを使用（推奨）

#### Windows

```bash
build.bat
```

実行すると以下の処理が自動で行われます：

1. 仮想環境の有効化
2. PyInstallerのインストール確認
3. 既存のビルドファイルのクリーンアップ
4. 実行可能ファイルのビルド
5. .envファイルのコピー

#### macOS/Linux

```bash
bash build.sh
```

実行すると以下の処理が自動で行われます：

1. 仮想環境の有効化
2. PyInstallerのインストール確認
3. 既存のビルドファイルのクリーンアップ
4. 実行可能ファイルのビルド
5. .envファイルのコピー（macOSの場合はアプリバンドル内）
6. 実行権限の付与（Linux）

### 方法2: 直接PyInstallerを実行

```bash
# 仮想環境を有効化（既に有効化済みの場合は不要）
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# PyInstallerを実行
pyinstaller youtube_analyzer.spec
```

---

## ビルド結果

### ディレクトリ構成

ビルドが成功すると、以下のディレクトリが作成されます：

```
youtube-video-analyzer/
├── build/                          # 一時ビルドファイル（削除可能）
└── dist/                           # 配布用ファイル
    └── YouTubeVideoAnalyzer/       # 実行可能ファイルとその依存関係
        ├── YouTubeVideoAnalyzer.exe    # 実行可能ファイル（Windows）
        ├── YouTubeVideoAnalyzer        # 実行可能ファイル（Linux）
        ├── _internal/                  # 依存ライブラリ
        ├── docs/                       # ドキュメント
        ├── .env.example                # 環境変数テンプレート
        └── README.md                   # README
```

**macOSの場合**:

```
dist/
└── YouTubeVideoAnalyzer.app        # アプリケーションバンドル
    └── Contents/
        └── MacOS/
            ├── YouTubeVideoAnalyzer    # 実行可能ファイル
            └── .env                    # 環境変数（コピーされる）
```

### ファイルサイズ

- **Windows**: 約100-150MB
- **macOS**: 約100-150MB（アプリバンドル）
- **Linux**: 約100-150MB

---

## 配布方法

### ステップ1: .envファイルの準備

**重要**: APIキーなどの機密情報を含む`.env`ファイルは配布**しないでください**。

配布時は`.env.example`のみを含め、ユーザーに以下を案内します：

1. `.env.example`を`.env`にリネーム
2. `YOUTUBE_API_KEY=your_api_key_here`にAPIキーを設定

### ステップ2: ZIPファイルの作成

#### Windows

```bash
# PowerShellを使用
Compress-Archive -Path dist\YouTubeVideoAnalyzer -DestinationPath YouTubeVideoAnalyzer-v1.0.0-windows.zip
```

または、エクスプローラーで`dist\YouTubeVideoAnalyzer`フォルダを右クリック → 「圧縮」

#### macOS

```bash
cd dist
zip -r YouTubeVideoAnalyzer-v1.0.0-macos.zip YouTubeVideoAnalyzer.app
```

または、Finderで`YouTubeVideoAnalyzer.app`を右クリック → 「圧縮」

#### Linux

```bash
cd dist
tar -czvf YouTubeVideoAnalyzer-v1.0.0-linux.tar.gz YouTubeVideoAnalyzer/
```

### ステップ3: READMEの追加

配布ZIPには以下のファイルを含めることを推奨します：

- 実行可能ファイル（`YouTubeVideoAnalyzer/`フォルダ）
- `README.md`（インストール・使用方法）
- `docs/installation-guide.md`（詳細なインストールガイド）
- `docs/user-manual.md`（ユーザーマニュアル）

### ステップ4: 配布

以下の方法で配布できます：

- **GitHub Releases**: GitHubのリリースページにZIPファイルをアップロード
- **Google Drive / Dropbox**: クラウドストレージで共有
- **メール**: 小規模な配布の場合

---

## 使用方法（エンドユーザー向け）

### Windows

1. ZIPファイルを展開
2. `YouTubeVideoAnalyzer`フォルダを開く
3. `.env.example`を`.env`にリネーム
4. `.env`ファイルを編集してYouTube APIキーを設定
5. `YouTubeVideoAnalyzer.exe`をダブルクリック

### macOS

1. ZIPファイルを展開
2. `YouTubeVideoAnalyzer.app`をアプリケーションフォルダにドラッグ&ドロップ（オプション）
3. `YouTubeVideoAnalyzer.app`を右クリック → 「パッケージの内容を表示」 → `Contents/MacOS/`に移動
4. `.env.example`を`.env`にリネームしてAPIキーを設定
5. `YouTubeVideoAnalyzer.app`をダブルクリック

**注意**: 初回起動時に「開発元を確認できないため開けません」と表示される場合：

- `YouTubeVideoAnalyzer.app`を右クリック → 「開く」 → 「開く」

### Linux

1. tarファイルを展開
   ```bash
   tar -xzvf YouTubeVideoAnalyzer-v1.0.0-linux.tar.gz
   ```
2. フォルダに移動
   ```bash
   cd YouTubeVideoAnalyzer
   ```
3. `.env.example`を`.env`にコピー
   ```bash
   cp .env.example .env
   ```
4. `.env`ファイルを編集してAPIキーを設定
   ```bash
   nano .env
   ```
5. 実行
   ```bash
   ./YouTubeVideoAnalyzer
   ```

---

## トラブルシューティング

### ビルド関連

#### 1. 「ModuleNotFoundError: No module named 'pyinstaller'」

**原因**: PyInstallerがインストールされていない

**解決策**:
```bash
pip install pyinstaller
# または
pip install -r requirements-dev.txt
```

#### 2. 「UnicodeDecodeError」（Windows）

**原因**: ファイルパスに日本語が含まれている

**解決策**:
- プロジェクトフォルダを英語のパスに移動（例: `C:\projects\youtube-video-analyzer`）

#### 3. ビルドが途中で止まる

**原因**: メモリ不足、または依存関係の問題

**解決策**:
```bash
# キャッシュをクリア
pyinstaller --clean youtube_analyzer.spec

# または一時ファイルを削除
rm -rf build dist
```

### 実行関連

#### 4. 実行可能ファイルが起動しない

**症状**: ダブルクリックしても何も起こらない

**解決策**:
- コマンドラインから実行してエラーメッセージを確認

**Windows**:
```bash
cd dist\YouTubeVideoAnalyzer
YouTubeVideoAnalyzer.exe
```

**macOS/Linux**:
```bash
cd dist/YouTubeVideoAnalyzer
./YouTubeVideoAnalyzer
```

#### 5. 「YouTube API キーが設定されていません」エラー

**原因**: `.env`ファイルが存在しない、またはAPIキーが設定されていない

**解決策**:
1. `.env.example`を`.env`にコピー
2. `.env`ファイルを開いて`YOUTUBE_API_KEY=your_api_key_here`を設定

#### 6. macOSで「開発元を確認できない」エラー

**原因**: Apple公式の開発者証明書で署名されていない

**解決策**:
1. `YouTubeVideoAnalyzer.app`を右クリック
2. 「開く」を選択
3. 警告ダイアログで「開く」をクリック

#### 7. Linuxで「Permission denied」エラー

**原因**: 実行権限がない

**解決策**:
```bash
chmod +x dist/YouTubeVideoAnalyzer/YouTubeVideoAnalyzer
```

### ビルドの最適化

#### ファイルサイズを削減したい場合

**.spec**ファイルで以下を調整：

```python
# UPX圧縮を有効化（デフォルトで有効）
upx=True,

# 不要なモジュールを除外
excludes=[
    'pytest',
    'black',
    'flake8',
    # ... 他の開発ツール
],
```

#### 起動速度を向上させたい場合

```python
# アーカイブを無効化（起動速度向上、ファイルサイズ増加）
noarchive=True,
```

---

## 参考資料

### 公式ドキュメント

- [PyInstaller公式ドキュメント](https://pyinstaller.org/en/stable/)
- [PyInstaller使い方ガイド](https://pyinstaller.org/en/stable/usage.html)

### プロジェクトドキュメント

- [README.md](../README.md) - プロジェクト概要
- [インストールガイド](./installation-guide.md) - Python環境でのインストール方法
- [ユーザーマニュアル](./user-manual.md) - 使い方

---

**最終更新**: 2025年11月27日
**バージョン**: 1.0.0 (Phase 5)
