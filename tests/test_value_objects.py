"""
値オブジェクトのテスト
"""
import pytest
from src.domain.value_objects import ViewCountRange, YouTubeVideoId, ChannelId


class TestViewCountRange:
    """ViewCountRangeのテスト"""

    def test_valid_range(self):
        """正常な範囲の作成"""
        range_obj = ViewCountRange(min_count=1000, max_count=10000)
        assert range_obj.min_count == 1000
        assert range_obj.max_count == 10000

    def test_negative_min_count(self):
        """負の最小値でエラー"""
        with pytest.raises(ValueError, match="最小再生回数は0以上を指定してください"):
            ViewCountRange(min_count=-100)

    def test_negative_max_count(self):
        """負の最大値でエラー"""
        with pytest.raises(ValueError, match="最大再生回数は0以上を指定してください"):
            ViewCountRange(max_count=-100)

    def test_invalid_range(self):
        """不正な範囲（最小 > 最大）でエラー"""
        with pytest.raises(ValueError, match="最小再生回数は最大再生回数以下を指定してください"):
            ViewCountRange(min_count=10000, max_count=1000)

    def test_contains_within_range(self):
        """範囲内の値を正しく判定"""
        range_obj = ViewCountRange(min_count=1000, max_count=10000)
        assert range_obj.contains(5000) is True
        assert range_obj.contains(1000) is True
        assert range_obj.contains(10000) is True

    def test_contains_outside_range(self):
        """範囲外の値を正しく判定"""
        range_obj = ViewCountRange(min_count=1000, max_count=10000)
        assert range_obj.contains(500) is False
        assert range_obj.contains(15000) is False

    def test_contains_with_only_min(self):
        """最小値のみの範囲"""
        range_obj = ViewCountRange(min_count=1000)
        assert range_obj.contains(5000) is True
        assert range_obj.contains(500) is False

    def test_contains_with_only_max(self):
        """最大値のみの範囲"""
        range_obj = ViewCountRange(max_count=10000)
        assert range_obj.contains(5000) is True
        assert range_obj.contains(15000) is False

    def test_immutable(self):
        """不変性のテスト"""
        range_obj = ViewCountRange(min_count=1000)
        with pytest.raises(Exception):  # dataclass frozenによるエラー
            range_obj.min_count = 2000


class TestYouTubeVideoId:
    """YouTubeVideoIdのテスト"""

    def test_valid_video_id(self):
        """正常な動画ID"""
        video_id = YouTubeVideoId(value="dQw4w9WgXcQ")
        assert video_id.value == "dQw4w9WgXcQ"

    def test_invalid_length(self):
        """不正な長さの動画ID"""
        with pytest.raises(ValueError, match="動画IDは11文字である必要があります"):
            YouTubeVideoId(value="short")

    def test_invalid_characters(self):
        """不正な文字を含む動画ID"""
        with pytest.raises(ValueError, match="動画IDに無効な文字が含まれています"):
            YouTubeVideoId(value="invalid@id!")

    def test_empty_video_id(self):
        """空の動画ID"""
        with pytest.raises(ValueError, match="動画IDは文字列である必要があります"):
            YouTubeVideoId(value="")

    def test_to_url(self):
        """URLへの変換"""
        video_id = YouTubeVideoId(value="dQw4w9WgXcQ")
        assert video_id.to_url() == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_immutable(self):
        """不変性のテスト"""
        video_id = YouTubeVideoId(value="dQw4w9WgXcQ")
        with pytest.raises(Exception):  # dataclass frozenによるエラー
            video_id.value = "other_id123"


class TestChannelId:
    """ChannelIdのテスト"""

    def test_valid_channel_id(self):
        """正常なチャンネルID"""
        channel_id = ChannelId(value="UC1234567890123456789012")
        assert channel_id.value == "UC1234567890123456789012"

    def test_invalid_prefix(self):
        """不正なプレフィックス"""
        with pytest.raises(ValueError, match="チャンネルIDの形式が正しくありません"):
            ChannelId(value="XX1234567890123456789012")

    def test_invalid_length(self):
        """不正な長さのチャンネルID"""
        with pytest.raises(ValueError, match="チャンネルIDの形式が正しくありません"):
            ChannelId(value="UC12345")

    def test_empty_channel_id(self):
        """空のチャンネルID"""
        with pytest.raises(ValueError, match="チャンネルIDは文字列である必要があります"):
            ChannelId(value="")

    def test_to_url(self):
        """URLへの変換"""
        channel_id = ChannelId(value="UC1234567890123456789012")
        assert channel_id.to_url() == "https://www.youtube.com/channel/UC1234567890123456789012"

    def test_immutable(self):
        """不変性のテスト"""
        channel_id = ChannelId(value="UC1234567890123456789012")
        with pytest.raises(Exception):  # dataclass frozenによるエラー
            channel_id.value = "UC9876543210987654321098"
