"""
データモデルのテスト
"""
import pytest
from datetime import datetime
from src.domain.models import (
    VideoInfo,
    SearchCriteria,
    VideoType,
    SearchPreset,
    SearchHistory
)


class TestVideoInfo:
    """VideoInfoのテスト"""

    def test_video_info_creation(self):
        """VideoInfoの生成テスト"""
        video = VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            channel_name="Test Channel",
            channel_id="UC1234567890123456789012",
            view_count=1000000,
            like_count=50000,
            comment_count=1000,
            published_at=datetime(2023, 1, 1),
            duration_seconds=210,
            is_short=False,
            description="Test description",
            tags=["test", "video"],
            thumbnail_url="https://example.com/thumb.jpg"
        )

        assert video.video_id == "dQw4w9WgXcQ"
        assert video.title == "Test Video"
        assert video.view_count == 1000000
        assert video.is_short is False

    def test_duration_formatted_with_hours(self):
        """動画の長さフォーマット（時間あり）"""
        video = VideoInfo(
            video_id="test",
            title="Test",
            url="https://example.com",
            channel_name="Test",
            channel_id="UC1234567890123456789012",
            view_count=0,
            like_count=0,
            comment_count=0,
            published_at=datetime.now(),
            duration_seconds=3665,  # 1時間1分5秒
            is_short=False
        )

        assert video.duration_formatted == "01:01:05"

    def test_duration_formatted_without_hours(self):
        """動画の長さフォーマット（時間なし）"""
        video = VideoInfo(
            video_id="test",
            title="Test",
            url="https://example.com",
            channel_name="Test",
            channel_id="UC1234567890123456789012",
            view_count=0,
            like_count=0,
            comment_count=0,
            published_at=datetime.now(),
            duration_seconds=125,  # 2分5秒
            is_short=False
        )

        assert video.duration_formatted == "02:05"

    def test_short_video_detection(self):
        """ショート動画の判定"""
        short_video = VideoInfo(
            video_id="test",
            title="Short",
            url="https://example.com",
            channel_name="Test",
            channel_id="UC1234567890123456789012",
            view_count=0,
            like_count=0,
            comment_count=0,
            published_at=datetime.now(),
            duration_seconds=45,
            is_short=True
        )

        assert short_video.is_short is True
        assert short_video.duration_seconds <= 60


class TestSearchCriteria:
    """SearchCriteriaのテスト"""

    def test_search_criteria_creation(self):
        """SearchCriteriaの生成テスト"""
        criteria = SearchCriteria(
            keyword="Python tutorial",
            min_view_count=1000,
            max_view_count=1000000,
            video_type=VideoType.NORMAL,
            max_results=50
        )

        assert criteria.keyword == "Python tutorial"
        assert criteria.min_view_count == 1000
        assert criteria.video_type == VideoType.NORMAL

    def test_validate_success(self):
        """バリデーション成功"""
        criteria = SearchCriteria(keyword="test", max_results=50)
        criteria.validate()  # 例外が発生しないことを確認

    def test_validate_empty_keyword(self):
        """空のキーワードでバリデーションエラー"""
        criteria = SearchCriteria(keyword="")
        with pytest.raises(ValueError, match="キーワードは必須です"):
            criteria.validate()

    def test_validate_invalid_max_results(self):
        """不正な最大取得件数でバリデーションエラー"""
        criteria = SearchCriteria(keyword="test", max_results=1000)
        with pytest.raises(ValueError, match="最大取得件数は1〜500の範囲で指定してください"):
            criteria.validate()

    def test_validate_negative_min_view_count(self):
        """負の最小再生回数でバリデーションエラー"""
        criteria = SearchCriteria(keyword="test", min_view_count=-100)
        with pytest.raises(ValueError, match="最小再生回数は0以上を指定してください"):
            criteria.validate()

    def test_validate_invalid_view_count_range(self):
        """不正な再生回数範囲でバリデーションエラー"""
        criteria = SearchCriteria(
            keyword="test",
            min_view_count=1000,
            max_view_count=500
        )
        with pytest.raises(ValueError, match="最小再生回数は最大再生回数以下を指定してください"):
            criteria.validate()

    def test_validate_invalid_date_range(self):
        """不正な公開日範囲でバリデーションエラー"""
        criteria = SearchCriteria(
            keyword="test",
            published_after=datetime(2023, 12, 31),
            published_before=datetime(2023, 1, 1)
        )
        with pytest.raises(ValueError, match="公開日開始は公開日終了以前を指定してください"):
            criteria.validate()

    def test_validate_invalid_order(self):
        """不正なソート順でバリデーションエラー"""
        criteria = SearchCriteria(keyword="test", order="invalid")
        with pytest.raises(ValueError, match="orderは"):
            criteria.validate()


class TestSearchPreset:
    """SearchPresetのテスト"""

    def test_preset_creation(self):
        """プリセットの生成テスト"""
        criteria = SearchCriteria(keyword="test", max_results=10)
        preset = SearchPreset(
            name="My Preset",
            criteria=criteria,
            preset_id=1,
            created_at=datetime.now()
        )

        assert preset.name == "My Preset"
        assert preset.criteria.keyword == "test"
        assert preset.preset_id == 1


class TestSearchHistory:
    """SearchHistoryのテスト"""

    def test_history_creation(self):
        """検索履歴の生成テスト"""
        criteria = SearchCriteria(keyword="test")
        history = SearchHistory(
            criteria=criteria,
            result_count=25,
            executed_at=datetime.now()
        )

        assert history.result_count == 25
        assert history.criteria.keyword == "test"
