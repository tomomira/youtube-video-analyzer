"""
動画検索サービスのテスト
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.application.video_search_service import VideoSearchService
from src.domain.models import VideoInfo, SearchCriteria, VideoType
from src.infrastructure.youtube_client import YouTubeAPIError


class TestVideoSearchService:
    """VideoSearchServiceのテスト"""

    def test_initialization_with_client(self):
        """クライアント指定での初期化"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)
        assert service.youtube_client == mock_client

    @patch('src.application.video_search_service.YouTubeClient')
    def test_initialization_without_client(self, mock_youtube_client_class):
        """クライアント未指定での初期化（自動生成）"""
        service = VideoSearchService()
        mock_youtube_client_class.assert_called_once()

    def test_search_success(self):
        """検索成功"""
        # モッククライアント
        mock_client = Mock()
        mock_videos = [
            VideoInfo(
                video_id="1", title="Test 1", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            )
        ]
        mock_client.search_videos.return_value = mock_videos

        # サービス実行
        service = VideoSearchService(youtube_client=mock_client)
        criteria = SearchCriteria(keyword="test")
        results = service.search(criteria)

        assert len(results) == 1
        assert results[0].video_id == "1"
        mock_client.search_videos.assert_called_once_with(criteria)

    def test_search_validation_error(self):
        """検索時のバリデーションエラー"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        # 不正な検索条件
        criteria = SearchCriteria(keyword="", max_results=50)

        with pytest.raises(ValueError):
            service.search(criteria)

    def test_search_api_error(self):
        """検索時のAPIエラー"""
        mock_client = Mock()
        mock_client.search_videos.side_effect = YouTubeAPIError("API Error")

        service = VideoSearchService(youtube_client=mock_client)
        criteria = SearchCriteria(keyword="test")

        with pytest.raises(YouTubeAPIError):
            service.search(criteria)

    def test_get_video_by_id_success(self):
        """動画ID検索成功"""
        mock_client = Mock()
        mock_video = VideoInfo(
            video_id="dQw4w9WgXcQ", title="Test Video", url="", channel_name="", channel_id="",
            view_count=1000, like_count=0, comment_count=0,
            published_at=datetime.now(), duration_seconds=100, is_short=False
        )
        mock_client.get_video_by_id.return_value = mock_video

        service = VideoSearchService(youtube_client=mock_client)
        result = service.get_video_by_id("dQw4w9WgXcQ")

        assert result is not None
        assert result.video_id == "dQw4w9WgXcQ"
        mock_client.get_video_by_id.assert_called_once_with("dQw4w9WgXcQ")

    def test_get_video_by_id_not_found(self):
        """動画ID検索で見つからない"""
        mock_client = Mock()
        mock_client.get_video_by_id.return_value = None

        service = VideoSearchService(youtube_client=mock_client)
        result = service.get_video_by_id("invalid_id")

        assert result is None

    def test_create_search_history(self):
        """検索履歴の作成"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        criteria = SearchCriteria(keyword="test")
        history = service.create_search_history(criteria, result_count=25)

        assert history.result_count == 25
        assert history.criteria.keyword == "test"
        assert history.executed_at is not None

    def test_filter_by_view_count(self):
        """再生回数フィルタリング"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        videos = [
            VideoInfo(
                video_id="1", title="V1", url="", channel_name="", channel_id="",
                view_count=500, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="2", title="V2", url="", channel_name="", channel_id="",
                view_count=5000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="3", title="V3", url="", channel_name="", channel_id="",
                view_count=50000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
        ]

        filtered = service.filter_by_view_count(videos, min_count=1000, max_count=10000)

        assert len(filtered) == 1
        assert filtered[0].video_id == "2"

    def test_filter_shorts(self):
        """ショート動画フィルタリング"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        videos = [
            VideoInfo(
                video_id="1", title="Short", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=30, is_short=True
            ),
            VideoInfo(
                video_id="2", title="Normal", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=300, is_short=False
            ),
        ]

        # ショート動画のみ
        shorts = service.filter_shorts(videos, shorts_only=True)
        assert len(shorts) == 1
        assert shorts[0].is_short is True

        # 通常動画のみ
        normals = service.filter_shorts(videos, shorts_only=False)
        assert len(normals) == 1
        assert normals[0].is_short is False

    def test_sort_by_view_count(self):
        """再生回数ソート"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        videos = [
            VideoInfo(
                video_id="1", title="V1", url="", channel_name="", channel_id="",
                view_count=5000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="2", title="V2", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="3", title="V3", url="", channel_name="", channel_id="",
                view_count=10000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
        ]

        # 降順
        sorted_desc = service.sort_by_view_count(videos, descending=True)
        assert sorted_desc[0].view_count == 10000
        assert sorted_desc[1].view_count == 5000
        assert sorted_desc[2].view_count == 1000

        # 昇順
        sorted_asc = service.sort_by_view_count(videos, descending=False)
        assert sorted_asc[0].view_count == 1000
        assert sorted_asc[1].view_count == 5000
        assert sorted_asc[2].view_count == 10000

    def test_sort_by_published_date(self):
        """公開日ソート"""
        mock_client = Mock()
        service = VideoSearchService(youtube_client=mock_client)

        videos = [
            VideoInfo(
                video_id="1", title="V1", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime(2023, 6, 1), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="2", title="V2", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime(2023, 1, 1), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="3", title="V3", url="", channel_name="", channel_id="",
                view_count=1000, like_count=0, comment_count=0,
                published_at=datetime(2023, 12, 1), duration_seconds=100, is_short=False
            ),
        ]

        # 降順（新しい順）
        sorted_desc = service.sort_by_published_date(videos, descending=True)
        assert sorted_desc[0].published_at.month == 12
        assert sorted_desc[1].published_at.month == 6
        assert sorted_desc[2].published_at.month == 1

        # 昇順（古い順）
        sorted_asc = service.sort_by_published_date(videos, descending=False)
        assert sorted_asc[0].published_at.month == 1
        assert sorted_asc[1].published_at.month == 6
        assert sorted_asc[2].published_at.month == 12
