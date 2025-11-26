"""
動画検索サービス

YouTube動画の検索ロジックを提供するアプリケーションサービス
"""
from typing import List, Optional
from datetime import datetime

from src.utils.logger import get_logger
from src.domain.models import VideoInfo, SearchCriteria, SearchHistory
from src.infrastructure.youtube_client import YouTubeClient, YouTubeAPIError

logger = get_logger(__name__)


class VideoSearchService:
    """
    動画検索サービス

    YouTube APIを使用した動画検索の高レベルインターフェースを提供
    """

    def __init__(self, youtube_client: Optional[YouTubeClient] = None):
        """
        初期化

        Args:
            youtube_client: YouTubeクライアント（未指定の場合は自動生成）
        """
        self.youtube_client = youtube_client or YouTubeClient()
        logger.info("VideoSearchServiceを初期化しました")

    def search(self, criteria: SearchCriteria) -> List[VideoInfo]:
        """
        検索条件に基づいて動画を検索

        Args:
            criteria: 検索条件

        Returns:
            List[VideoInfo]: 動画情報リスト

        Raises:
            ValueError: バリデーションエラー
            YouTubeAPIError: API呼び出しエラー
        """
        logger.info(f"動画検索を開始: キーワード='{criteria.keyword}'")

        # バリデーション
        criteria.validate()

        # YouTube APIで検索
        try:
            videos = self.youtube_client.search_videos(criteria)
            logger.info(f"検索完了: {len(videos)}件の動画を取得")
            return videos

        except YouTubeAPIError as e:
            logger.error(f"動画検索に失敗: {e}")
            raise

    def get_video_by_id(self, video_id: str) -> Optional[VideoInfo]:
        """
        動画IDから動画情報を取得

        Args:
            video_id: YouTube動画ID

        Returns:
            Optional[VideoInfo]: 動画情報（見つからない場合はNone）

        Raises:
            YouTubeAPIError: API呼び出しエラー
        """
        logger.info(f"動画IDで検索: {video_id}")

        try:
            video = self.youtube_client.get_video_by_id(video_id)
            if video:
                logger.info(f"動画を取得: {video.title}")
            else:
                logger.warning(f"動画ID {video_id} が見つかりませんでした")
            return video

        except YouTubeAPIError as e:
            logger.error(f"動画取得に失敗: {e}")
            raise

    def create_search_history(self, criteria: SearchCriteria, result_count: int) -> SearchHistory:
        """
        検索履歴を作成

        Args:
            criteria: 検索条件
            result_count: 検索結果件数

        Returns:
            SearchHistory: 検索履歴オブジェクト
        """
        history = SearchHistory(
            criteria=criteria,
            result_count=result_count,
            executed_at=datetime.now()
        )
        logger.info(f"検索履歴を作成: キーワード='{criteria.keyword}', 結果={result_count}件")
        return history

    def filter_by_view_count(
        self,
        videos: List[VideoInfo],
        min_count: Optional[int] = None,
        max_count: Optional[int] = None
    ) -> List[VideoInfo]:
        """
        再生回数でフィルタリング

        Args:
            videos: 動画情報リスト
            min_count: 最小再生回数
            max_count: 最大再生回数

        Returns:
            List[VideoInfo]: フィルタリング後の動画リスト
        """
        filtered = []

        for video in videos:
            if min_count is not None and video.view_count < min_count:
                continue
            if max_count is not None and video.view_count > max_count:
                continue
            filtered.append(video)

        logger.info(f"再生回数フィルタリング: {len(videos)}件 → {len(filtered)}件")
        return filtered

    def filter_shorts(self, videos: List[VideoInfo], shorts_only: bool = True) -> List[VideoInfo]:
        """
        ショート動画でフィルタリング

        Args:
            videos: 動画情報リスト
            shorts_only: Trueの場合ショート動画のみ、Falseの場合通常動画のみ

        Returns:
            List[VideoInfo]: フィルタリング後の動画リスト
        """
        filtered = [v for v in videos if v.is_short == shorts_only]
        logger.info(f"ショート動画フィルタリング: {len(videos)}件 → {len(filtered)}件")
        return filtered

    def sort_by_view_count(self, videos: List[VideoInfo], descending: bool = True) -> List[VideoInfo]:
        """
        再生回数でソート

        Args:
            videos: 動画情報リスト
            descending: Trueの場合降順、Falseの場合昇順

        Returns:
            List[VideoInfo]: ソート済み動画リスト
        """
        sorted_videos = sorted(videos, key=lambda v: v.view_count, reverse=descending)
        logger.info(f"再生回数でソート: {len(videos)}件")
        return sorted_videos

    def sort_by_published_date(self, videos: List[VideoInfo], descending: bool = True) -> List[VideoInfo]:
        """
        公開日でソート

        Args:
            videos: 動画情報リスト
            descending: Trueの場合降順（新しい順）、Falseの場合昇順（古い順）

        Returns:
            List[VideoInfo]: ソート済み動画リスト
        """
        sorted_videos = sorted(videos, key=lambda v: v.published_at, reverse=descending)
        logger.info(f"公開日でソート: {len(videos)}件")
        return sorted_videos
