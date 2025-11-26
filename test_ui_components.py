"""
UI コンポーネントのテスト

実際のGUIは起動せずに、UIコンポーネントが正しく初期化できることを確認
"""
import sys
import os
from datetime import datetime

# パスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.domain.models import SearchCriteria, VideoInfo, VideoType


def test_search_criteria_creation():
    """SearchCriteriaの作成テスト"""
    print("1. SearchCriteria作成テスト...")
    criteria = SearchCriteria(
        keyword="Python tutorial",
        min_view_count=1000,
        max_view_count=100000,
        video_type=VideoType.NORMAL,
        max_results=10
    )
    print(f"  ✓ キーワード: {criteria.keyword}")
    print(f"  ✓ 再生回数範囲: {criteria.min_view_count} 〜 {criteria.max_view_count}")
    print(f"  ✓ 動画タイプ: {criteria.video_type}")
    print()


def test_video_info_display():
    """VideoInfo の表示形式テスト"""
    print("2. VideoInfo表示形式テスト...")
    video = VideoInfo(
        video_id="dQw4w9WgXcQ",
        title="Sample Video Title",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        channel_name="Test Channel",
        channel_id="UC1234567890123456789012",
        view_count=1234567,
        like_count=50000,
        comment_count=1000,
        published_at=datetime(2023, 1, 1, 12, 0, 0),
        duration_seconds=210,
        is_short=False,
        description="Test description",
        tags=["test", "video"],
        thumbnail_url="https://example.com/thumb.jpg"
    )

    print(f"  ✓ タイトル: {video.title}")
    print(f"  ✓ チャンネル: {video.channel_name}")
    print(f"  ✓ 再生回数: {video.view_count:,}回")
    print(f"  ✓ 長さ: {video.duration_formatted}")
    print(f"  ✓ 公開日: {video.published_at.strftime('%Y-%m-%d')}")
    print(f"  ✓ 種類: {'ショート' if video.is_short else '通常'}")
    print()


def test_short_video():
    """ショート動画の表示形式テスト"""
    print("3. ショート動画表示テスト...")
    short_video = VideoInfo(
        video_id="short123456",
        title="Short Video",
        url="https://www.youtube.com/watch?v=short123456",
        channel_name="Short Channel",
        channel_id="UC9876543210987654321098",
        view_count=500000,
        like_count=25000,
        comment_count=500,
        published_at=datetime(2024, 1, 1),
        duration_seconds=45,
        is_short=True
    )

    print(f"  ✓ タイトル: {short_video.title}")
    print(f"  ✓ 再生回数: {short_video.view_count:,}回")
    print(f"  ✓ 長さ: {short_video.duration_formatted}")
    print(f"  ✓ 種類: {'ショート' if short_video.is_short else '通常'}")
    print()


def test_validation():
    """バリデーションテスト"""
    print("4. バリデーションテスト...")

    # 正常なケース
    try:
        criteria = SearchCriteria(keyword="test", max_results=50)
        criteria.validate()
        print("  ✓ 正常な検索条件はバリデーション通過")
    except ValueError as e:
        print(f"  ✗ エラー: {e}")

    # エラーケース: 空のキーワード
    try:
        criteria = SearchCriteria(keyword="", max_results=50)
        criteria.validate()
        print("  ✗ 空のキーワードがバリデーションを通過してしまった")
    except ValueError:
        print("  ✓ 空のキーワードは正しくエラーになる")

    # エラーケース: 不正な最大件数
    try:
        criteria = SearchCriteria(keyword="test", max_results=1000)
        criteria.validate()
        print("  ✗ 不正な最大件数がバリデーションを通過してしまった")
    except ValueError:
        print("  ✓ 不正な最大件数は正しくエラーになる")

    print()


def test_imports():
    """モジュールのインポートテスト"""
    print("5. UIコンポーネントのインポートテスト...")
    try:
        from src.ui.search_panel import SearchPanel
        print("  ✓ SearchPanel インポート成功")
    except Exception as e:
        print(f"  ✗ SearchPanel インポートエラー: {e}")

    try:
        from src.ui.result_panel import ResultPanel
        print("  ✓ ResultPanel インポート成功")
    except Exception as e:
        print(f"  ✗ ResultPanel インポートエラー: {e}")

    try:
        from src.ui.main_window import MainWindow
        print("  ✓ MainWindow インポート成功")
    except Exception as e:
        print(f"  ✗ MainWindow インポートエラー: {e}")

    print()


def main():
    print("=" * 60)
    print("YouTube Video Analyzer - UIコンポーネントテスト")
    print("=" * 60)
    print()

    test_imports()
    test_search_criteria_creation()
    test_video_info_display()
    test_short_video()
    test_validation()

    print("=" * 60)
    print("すべてのテストが完了しました")
    print("=" * 60)


if __name__ == "__main__":
    main()
