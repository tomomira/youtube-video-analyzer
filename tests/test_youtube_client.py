"""
YouTubeクライアントのテスト

注意: これらのテストはモックを使用し、実際のAPIを呼び出しません
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.infrastructure.youtube_client import YouTubeClient, YouTubeAPIError
from src.domain.models import SearchCriteria, VideoType


class TestYouTubeClient:
    """YouTubeClientのテスト"""

    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('src.infrastructure.youtube_client.build')
    def test_initialization_success(self, mock_build):
        """正常な初期化"""
        mock_build.return_value = MagicMock()
        client = YouTubeClient()
        assert client.api_key == 'test_api_key'
        mock_build.assert_called_once_with("youtube", "v3", developerKey='test_api_key')

    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_no_api_key(self):
        """APIキーなしで初期化エラー"""
        with pytest.raises(YouTubeAPIError, match="YOUTUBE_API_KEYが設定されていません"):
            YouTubeClient()

    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('src.infrastructure.youtube_client.build')
    def test_parse_video_item(self, mock_build):
        """動画情報のパース"""
        mock_build.return_value = MagicMock()
        client = YouTubeClient()

        # モックのAPIレスポンス
        item = {
            "id": "dQw4w9WgXcQ",
            "snippet": {
                "title": "Test Video",
                "channelTitle": "Test Channel",
                "channelId": "UC1234567890123456789012",
                "publishedAt": "2023-01-01T00:00:00Z",
                "description": "Test description",
                "tags": ["test", "video"],
                "thumbnails": {
                    "high": {
                        "url": "https://example.com/thumb.jpg"
                    }
                }
            },
            "statistics": {
                "viewCount": "1000000",
                "likeCount": "50000",
                "commentCount": "1000"
            },
            "contentDetails": {
                "duration": "PT3M30S"  # 3分30秒
            }
        }

        video = client._parse_video_item(item)

        assert video is not None
        assert video.video_id == "dQw4w9WgXcQ"
        assert video.title == "Test Video"
        assert video.view_count == 1000000
        assert video.duration_seconds == 210  # 3分30秒 = 210秒
        assert video.is_short is False

    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('src.infrastructure.youtube_client.build')
    def test_parse_short_video(self, mock_build):
        """ショート動画のパース"""
        mock_build.return_value = MagicMock()
        client = YouTubeClient()

        # ショート動画（60秒以下）
        item = {
            "id": "short_id123",
            "snippet": {
                "title": "Short Video",
                "channelTitle": "Test Channel",
                "channelId": "UC1234567890123456789012",
                "publishedAt": "2023-01-01T00:00:00Z",
                "description": "",
                "thumbnails": {}
            },
            "statistics": {
                "viewCount": "10000",
                "likeCount": "500",
                "commentCount": "10"
            },
            "contentDetails": {
                "duration": "PT45S"  # 45秒
            }
        }

        video = client._parse_video_item(item)

        assert video is not None
        assert video.duration_seconds == 45
        assert video.is_short is True

    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('src.infrastructure.youtube_client.build')
    def test_filter_videos_by_view_count(self, mock_build):
        """再生回数によるフィルタリング"""
        mock_build.return_value = MagicMock()
        client = YouTubeClient()

        # テスト用の動画リスト
        from src.domain.models import VideoInfo

        videos = [
            VideoInfo(
                video_id="1", title="Video 1", url="", channel_name="", channel_id="",
                view_count=500, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="2", title="Video 2", url="", channel_name="", channel_id="",
                view_count=5000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
            VideoInfo(
                video_id="3", title="Video 3", url="", channel_name="", channel_id="",
                view_count=50000, like_count=0, comment_count=0,
                published_at=datetime.now(), duration_seconds=100, is_short=False
            ),
        ]

        criteria = SearchCriteria(
            keyword="test",
            min_view_count=1000,
            max_view_count=10000
        )

        filtered = client._filter_videos(videos, criteria)

        assert len(filtered) == 1
        assert filtered[0].video_id == "2"

    @patch.dict('os.environ', {'YOUTUBE_API_KEY': 'test_api_key'})
    @patch('src.infrastructure.youtube_client.build')
    def test_filter_videos_by_type(self, mock_build):
        """動画タイプによるフィルタリング"""
        mock_build.return_value = MagicMock()
        client = YouTubeClient()

        from src.domain.models import VideoInfo

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
        criteria_short = SearchCriteria(keyword="test", video_type=VideoType.SHORT)
        filtered_short = client._filter_videos(videos, criteria_short)
        assert len(filtered_short) == 1
        assert filtered_short[0].is_short is True

        # 通常動画のみ
        criteria_normal = SearchCriteria(keyword="test", video_type=VideoType.NORMAL)
        filtered_normal = client._filter_videos(videos, criteria_normal)
        assert len(filtered_normal) == 1
        assert filtered_normal[0].is_short is False

        # すべて
        criteria_all = SearchCriteria(keyword="test", video_type=VideoType.ALL)
        filtered_all = client._filter_videos(videos, criteria_all)
        assert len(filtered_all) == 2
