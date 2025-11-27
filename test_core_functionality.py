"""
コア機能の動作確認スクリプト（GUIなし）

このスクリプトは、GUIを使わずにYouTube Video Analyzerの
コア機能が正しく動作するか確認します。
"""
import os
import sys
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

print("=" * 60)
print("YouTube Video Analyzer - コア機能動作確認")
print("=" * 60)
print()

# 1. 環境変数の確認
print("[1/5] 環境変数の確認...")
api_key = os.getenv("YOUTUBE_API_KEY")
if api_key and api_key != "your_api_key_here":
    print(f"  ✓ YouTube APIキー: 設定済み（{len(api_key)}文字）")
else:
    print("  ⚠️  YouTube APIキー: 未設定または初期値")
    print("     .envファイルでYOUTUBE_API_KEYを設定してください")

print()

# 2. モジュールのインポート確認
print("[2/5] モジュールのインポート確認...")
try:
    from src.domain.models import VideoInfo, SearchCriteria, VideoType
    print("  ✓ domain.models")

    from src.infrastructure.youtube_client import YouTubeClient
    print("  ✓ infrastructure.youtube_client")

    from src.application.video_search_service import VideoSearchService
    print("  ✓ application.video_search_service")

    from src.application.preset_service import PresetService
    print("  ✓ application.preset_service")

    from src.application.history_service import HistoryService
    print("  ✓ application.history_service")

    from src.infrastructure.excel_exporter import ExcelExporter
    print("  ✓ infrastructure.excel_exporter")

    print("  ✅ すべてのモジュールが正常にインポートされました")
except ImportError as e:
    print(f"  ❌ インポートエラー: {e}")
    sys.exit(1)

print()

# 3. データモデルの確認
print("[3/5] データモデルの確認...")
try:
    # SearchCriteriaの作成
    criteria = SearchCriteria(
        keyword="Python tutorial",
        min_view_count=1000,
        max_view_count=100000,
        video_type=VideoType.NORMAL,
        max_results=10
    )
    print(f"  ✓ SearchCriteria作成成功")
    print(f"    - キーワード: {criteria.keyword}")
    print(f"    - 再生回数範囲: {criteria.min_view_count:,} 〜 {criteria.max_view_count:,}")
    print(f"    - 動画タイプ: {criteria.video_type.value}")

except Exception as e:
    print(f"  ❌ データモデルエラー: {e}")
    sys.exit(1)

print()

# 4. データベースサービスの確認
print("[4/5] データベースサービスの確認...")
try:
    # PresetServiceのテスト
    preset_service = PresetService("test_core_check.db")
    preset = preset_service.save_preset("テストプリセット", criteria)
    print(f"  ✓ PresetService: プリセット保存成功")

    loaded_preset = preset_service.load_preset("テストプリセット")
    if loaded_preset and loaded_preset.name == "テストプリセット":
        print(f"  ✓ PresetService: プリセット読み込み成功")

    # HistoryServiceのテスト
    history_service = HistoryService("test_core_check.db")
    history = history_service.add_history(criteria, result_count=42)
    print(f"  ✓ HistoryService: 履歴追加成功")

    recent = history_service.get_recent_history(limit=1)
    if len(recent) > 0:
        print(f"  ✓ HistoryService: 履歴取得成功")

    # クリーンアップ
    import os
    if os.path.exists("test_core_check.db"):
        os.remove("test_core_check.db")
        print(f"  ✓ テストデータベースをクリーンアップ")

except Exception as e:
    print(f"  ❌ データベースサービスエラー: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 5. YouTube APIクライアントの確認（APIキーが設定されている場合のみ）
print("[5/5] YouTube APIクライアントの確認...")
if api_key and api_key != "your_api_key_here":
    try:
        client = YouTubeClient(api_key)
        print("  ✓ YouTubeClient初期化成功")
        print("  ⚠️  実際のAPI呼び出しはクォータを消費するため、スキップします")
        print("     実際の検索テストを行う場合は、GUIアプリを起動してください")
    except Exception as e:
        print(f"  ❌ YouTubeClientエラー: {e}")
else:
    print("  ⚠️  APIキーが未設定のため、YouTubeClientのテストをスキップします")

print()
print("=" * 60)
print("✅ コア機能の動作確認完了！")
print("=" * 60)
print()
print("次のステップ:")
print("  1. .envファイルでYouTube APIキーを設定（まだの場合）")
print("  2. GUIアプリケーションを起動:")
if sys.platform == "win32":
    print("     python src/main.py")
else:
    print("     # Windows環境で実行:")
    print("     python src/main.py")
    print()
    print("     # WSL環境では、Windowsのコマンドプロンプトまたは")
    print("     # PowerShellから実行することを推奨します")
print()
