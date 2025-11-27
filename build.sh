#!/bin/bash
# ========================================
# YouTube Video Analyzer ビルドスクリプト（macOS/Linux用）
# ========================================
#
# このスクリプトは、PyInstallerを使用してスタンドアロン実行可能ファイルを作成します。
#
# 前提条件:
#   - Python 3.10以上がインストールされていること
#   - 仮想環境が作成されていること
#
# 使い方:
#   bash build.sh
#

set -e  # エラーが発生したら即座に終了

echo "========================================"
echo "YouTube Video Analyzer ビルドスクリプト"
echo "========================================"
echo ""

# 仮想環境の有効化
echo "[1/5] 仮想環境を有効化しています..."
if [ ! -d "venv" ]; then
    echo "エラー: venvフォルダが見つかりません"
    echo "まず 'python -m venv venv' で仮想環境を作成してください"
    exit 1
fi

source venv/bin/activate

# PyInstallerのインストール確認
echo "[2/5] PyInstallerをインストールしています..."
pip install pyinstaller

# 既存のビルドファイルをクリーンアップ
echo "[3/5] 既存のビルドファイルをクリーンアップしています..."
rm -rf build dist

# PyInstallerでビルド
echo "[4/5] 実行可能ファイルをビルドしています..."
echo "このプロセスには数分かかる場合があります。お待ちください..."
pyinstaller youtube_analyzer.spec

# .envファイルの確認と警告
echo "[5/5] ビルド後の設定を確認しています..."
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: .envファイルが見つかりません"
    echo "ビルドされた実行可能ファイルを使用する前に、.env.exampleをコピーして.envを作成し、"
    echo "YouTube APIキーを設定してください。"
    echo ""
fi

# .envファイルをdistフォルダにコピー（存在する場合）
if [ -f ".env" ]; then
    # macOSの場合
    if [ -d "dist/YouTubeVideoAnalyzer.app" ]; then
        cp .env dist/YouTubeVideoAnalyzer.app/Contents/MacOS/.env
        echo ".envファイルをアプリバンドルにコピーしました"
    else
        # Linuxの場合
        cp .env dist/YouTubeVideoAnalyzer/.env
        echo ".envファイルをコピーしました"
    fi
fi

# 実行権限を付与（Linux用）
if [ "$(uname)" == "Linux" ]; then
    chmod +x dist/YouTubeVideoAnalyzer/YouTubeVideoAnalyzer
fi

# 完了メッセージ
echo ""
echo "========================================"
echo "ビルドが完了しました！"
echo "========================================"
echo ""

# OSに応じてメッセージを変更
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    echo "実行可能ファイルの場所:"
    echo "  dist/YouTubeVideoAnalyzer.app"
    echo ""
    echo "次の手順:"
    echo "  1. Finderでdist/YouTubeVideoAnalyzer.appを開く"
    echo "  2. アプリケーションフォルダにドラッグ&ドロップ（オプション）"
    echo "  3. YouTubeVideoAnalyzer.appをダブルクリックして起動"
    echo ""
    echo "注意:"
    echo "  初回起動時に「開発元を確認できないため開けません」と表示される場合:"
    echo "  右クリック → 開く → 開く で起動してください"
else
    # Linux
    echo "実行可能ファイルの場所:"
    echo "  dist/YouTubeVideoAnalyzer/YouTubeVideoAnalyzer"
    echo ""
    echo "次の手順:"
    echo "  1. cd dist/YouTubeVideoAnalyzer"
    echo "  2. .envファイルにYouTube APIキーを設定（まだの場合）"
    echo "  3. ./YouTubeVideoAnalyzer で起動"
fi

echo ""
