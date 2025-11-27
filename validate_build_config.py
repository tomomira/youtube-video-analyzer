"""
ビルド設定の検証スクリプト

PyInstallerの.specファイルとビルドスクリプトが正しく設定されているか確認します。
"""
import os
import sys


def validate_spec_file():
    """youtube_analyzer.specファイルの存在と内容を検証"""
    print("[1/5] .specファイルを検証しています...")

    spec_file = "youtube_analyzer.spec"
    if not os.path.exists(spec_file):
        print(f"  ❌ エラー: {spec_file} が見つかりません")
        return False

    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 重要な設定をチェック
    checks = [
        ("src/main.py", "エントリーポイント"),
        ("hiddenimports", "隠れたインポート"),
        ("tkinter", "tkinterライブラリ"),
        ("googleapiclient", "Google APIクライアント"),
    ]

    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}: OK")
        else:
            print(f"  ❌ {description}: 見つかりません")
            all_ok = False

    return all_ok


def validate_build_scripts():
    """ビルドスクリプトの存在を検証"""
    print("\n[2/5] ビルドスクリプトを検証しています...")

    scripts = {
        "build.bat": "Windows用ビルドスクリプト",
        "build.sh": "macOS/Linux用ビルドスクリプト",
    }

    all_ok = True
    for script, description in scripts.items():
        if os.path.exists(script):
            print(f"  ✓ {description}: 存在します")

            # Linuxの場合、実行権限をチェック
            if script == "build.sh" and sys.platform != "win32":
                if os.access(script, os.X_OK):
                    print(f"    ✓ 実行権限: あり")
                else:
                    print(f"    ❌ 実行権限: なし")
                    all_ok = False
        else:
            print(f"  ❌ {description}: 見つかりません")
            all_ok = False

    return all_ok


def validate_source_files():
    """ソースファイルの存在を検証"""
    print("\n[3/5] ソースファイルを検証しています...")

    required_files = [
        "src/main.py",
        "src/ui/main_window.py",
        "src/ui/search_panel.py",
        "src/ui/result_panel.py",
        "src/application/video_search_service.py",
        "src/infrastructure/youtube_client.py",
    ]

    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ {file_path}: 見つかりません")
            all_ok = False

    return all_ok


def validate_dependencies():
    """依存パッケージの存在を検証"""
    print("\n[4/5] 依存パッケージを検証しています...")

    required_packages = [
        "tkinter",
        "googleapiclient",
        "openpyxl",
        "dotenv",
        "isodate",
    ]

    all_ok = True
    for package in required_packages:
        try:
            if package == "tkinter":
                __import__("tkinter")
            elif package == "dotenv":
                __import__("dotenv")
            elif package == "googleapiclient":
                __import__("googleapiclient.discovery")
            else:
                __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package}: インストールされていません")
            all_ok = False

    return all_ok


def validate_documentation():
    """ドキュメントの存在を検証"""
    print("\n[5/5] ドキュメントを検証しています...")

    docs = [
        "README.md",
        ".env.example",
        "docs/installation-guide.md",
        "docs/user-manual.md",
        "docs/build-guide.md",
    ]

    all_ok = True
    for doc in docs:
        if os.path.exists(doc):
            print(f"  ✓ {doc}")
        else:
            print(f"  ❌ {doc}: 見つかりません")
            all_ok = False

    return all_ok


def main():
    """メイン関数"""
    print("=" * 60)
    print("YouTube Video Analyzer ビルド設定検証")
    print("=" * 60)
    print()

    results = []

    results.append(("仕様ファイル", validate_spec_file()))
    results.append(("ビルドスクリプト", validate_build_scripts()))
    results.append(("ソースファイル", validate_source_files()))
    results.append(("依存パッケージ", validate_dependencies()))
    results.append(("ドキュメント", validate_documentation()))

    print("\n" + "=" * 60)
    print("検証結果")
    print("=" * 60)

    all_passed = True
    for category, passed in results:
        status = "✓ 合格" if passed else "❌ 不合格"
        print(f"{category:20s}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n✅ すべての検証に合格しました！")
        print("ビルドを実行できます:")
        print("  - Windows: build.bat")
        print("  - macOS/Linux: bash build.sh")
        return 0
    else:
        print("\n❌ いくつかの検証に失敗しました。")
        print("上記のエラーを修正してから再度実行してください。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
