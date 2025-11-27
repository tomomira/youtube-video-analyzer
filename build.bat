@echo off
REM ========================================
REM YouTube Video Analyzer ビルドスクリプト（Windows用）
REM ========================================
REM
REM このスクリプトは、PyInstallerを使用してスタンドアロン実行可能ファイルを作成します。
REM
REM 前提条件:
REM   - Python 3.10以上がインストールされていること
REM   - 仮想環境が作成されていること
REM
REM 使い方:
REM   build.bat
REM

echo ========================================
echo YouTube Video Analyzer ビルドスクリプト
echo ========================================
echo.

REM 仮想環境の有効化
echo [1/5] 仮想環境を有効化しています...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo エラー: 仮想環境の有効化に失敗しました
    echo venvフォルダが存在するか確認してください
    pause
    exit /b 1
)

REM PyInstallerのインストール確認
echo [2/5] PyInstallerをインストールしています...
pip install pyinstaller
if errorlevel 1 (
    echo エラー: PyInstallerのインストールに失敗しました
    pause
    exit /b 1
)

REM 既存のビルドファイルをクリーンアップ
echo [3/5] 既存のビルドファイルをクリーンアップしています...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM PyInstallerでビルド
echo [4/5] 実行可能ファイルをビルドしています...
echo このプロセスには数分かかる場合があります。お待ちください...
pyinstaller youtube_analyzer.spec
if errorlevel 1 (
    echo エラー: ビルドに失敗しました
    pause
    exit /b 1
)

REM .envファイルの確認と警告
echo [5/5] ビルド後の設定を確認しています...
if not exist .env (
    echo.
    echo 警告: .envファイルが見つかりません
    echo ビルドされた実行可能ファイルを使用する前に、.env.exampleをコピーして.envを作成し、
    echo YouTube APIキーを設定してください。
    echo.
)

REM .envファイルをdistフォルダにコピー（存在する場合）
if exist .env (
    copy .env dist\YouTubeVideoAnalyzer\.env
    echo .envファイルをコピーしました
)

REM 完了メッセージ
echo.
echo ========================================
echo ビルドが完了しました！
echo ========================================
echo.
echo 実行可能ファイルの場所:
echo   dist\YouTubeVideoAnalyzer\YouTubeVideoAnalyzer.exe
echo.
echo 次の手順:
echo   1. dist\YouTubeVideoAnalyzer フォルダに移動
echo   2. .envファイルにYouTube APIキーを設定（まだの場合）
echo   3. YouTubeVideoAnalyzer.exe をダブルクリックして起動
echo.
pause
