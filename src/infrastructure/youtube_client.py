"""
YouTube APIクライアント

YouTube Data API v3とのやり取りを担当
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import isodate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils.logger import get_logger
from src.domain.models import VideoInfo, SearchCriteria, VideoType

logger = get_logger(__name__)


class YouTubeAPIError(Exception):
    """YouTube API関連のエラー"""
    pass


class YouTubeClient:
    """
    YouTube Data API v3クライアント

    Attributes:
        api_key: YouTube Data API v3のAPIキー
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初期化

        Args:
            api_key: APIキー（未指定の場合は環境変数から取得）

        Raises:
            YouTubeAPIError: APIキーが取得できない場合
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise YouTubeAPIError("YOUTUBE_API_KEYが設定されていません")

        try:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
            logger.info("YouTube APIクライアントを初期化しました")
        except Exception as e:
            logger.error(f"YouTube APIクライアントの初期化に失敗: {e}", exc_info=True)
            raise YouTubeAPIError(f"YouTube APIクライアントの初期化に失敗: {e}")

    def search_videos(self, criteria: SearchCriteria) -> List[VideoInfo]:
        """
        検索条件に基づいて動画を検索

        Args:
            criteria: 検索条件

        Returns:
            List[VideoInfo]: 動画情報リスト

        Raises:
            YouTubeAPIError: API呼び出しエラー
        """
        criteria.validate()

        logger.info(f"動画検索開始: キーワード='{criteria.keyword}', 最大取得数={criteria.max_results}")

        try:
            # Step 1: search.list APIで動画IDを取得
            video_ids = self._search_video_ids(criteria)

            if not video_ids:
                logger.info("検索結果が0件でした")
                return []

            logger.info(f"検索結果: {len(video_ids)}件の動画IDを取得")

            # Step 2: videos.list APIで動画詳細を取得
            videos = self._get_video_details(video_ids)

            # Step 3: フィルタリング（再生回数、動画タイプ）
            filtered_videos = self._filter_videos(videos, criteria)

            logger.info(f"フィルタリング後: {len(filtered_videos)}件")

            return filtered_videos[:criteria.max_results]

        except HttpError as e:
            logger.error(f"YouTube API呼び出しエラー: {e}", exc_info=True)
            raise YouTubeAPIError(f"YouTube API呼び出しエラー: {e}")
        except Exception as e:
            logger.error(f"予期しないエラー: {e}", exc_info=True)
            raise YouTubeAPIError(f"予期しないエラー: {e}")

    def _search_video_ids(self, criteria: SearchCriteria) -> List[str]:
        """
        search.list APIで動画IDを取得

        Args:
            criteria: 検索条件

        Returns:
            List[str]: 動画IDリスト
        """
        video_ids = []
        next_page_token = None
        max_iterations = 10  # 無限ループ防止

        # 1リクエストあたり最大50件まで取得可能
        per_page = min(criteria.max_results, 50)

        for _ in range(max_iterations):
            request_params = {
                "part": "id",
                "q": criteria.keyword,
                "type": "video",
                "maxResults": per_page,
                "order": criteria.order,
                "regionCode": criteria.region_code,
                "relevanceLanguage": criteria.language,
            }

            # 公開日範囲
            if criteria.published_after:
                request_params["publishedAfter"] = criteria.published_after.isoformat() + "Z"
            if criteria.published_before:
                request_params["publishedBefore"] = criteria.published_before.isoformat() + "Z"

            # ページネーション
            if next_page_token:
                request_params["pageToken"] = next_page_token

            response = self.youtube.search().list(**request_params).execute()

            # 動画IDを抽出
            for item in response.get("items", []):
                video_id = item["id"].get("videoId")
                if video_id:
                    video_ids.append(video_id)

            # 次ページがあるかチェック
            next_page_token = response.get("nextPageToken")
            if not next_page_token or len(video_ids) >= criteria.max_results:
                break

        return video_ids[:criteria.max_results]

    def _get_video_details(self, video_ids: List[str]) -> List[VideoInfo]:
        """
        videos.list APIで動画詳細を取得

        Args:
            video_ids: 動画IDリスト

        Returns:
            List[VideoInfo]: 動画情報リスト
        """
        videos = []

        # videos.list APIは1リクエストで最大50件まで
        batch_size = 50

        for i in range(0, len(video_ids), batch_size):
            batch_ids = video_ids[i:i + batch_size]
            response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch_ids)
            ).execute()

            for item in response.get("items", []):
                video_info = self._parse_video_item(item)
                if video_info:
                    videos.append(video_info)

        return videos

    def _parse_video_item(self, item: Dict[str, Any]) -> Optional[VideoInfo]:
        """
        APIレスポンスからVideoInfoオブジェクトを生成

        Args:
            item: videos.list APIのレスポンスアイテム

        Returns:
            Optional[VideoInfo]: 動画情報（パースエラー時はNone）
        """
        try:
            video_id = item["id"]
            snippet = item["snippet"]
            statistics = item["statistics"]
            content_details = item["contentDetails"]

            # 動画の長さをパース（ISO 8601形式 → 秒数）
            duration_str = content_details["duration"]
            duration_seconds = int(isodate.parse_duration(duration_str).total_seconds())

            # ショート動画判定（60秒以下）
            is_short = duration_seconds <= 60

            # 公開日時をパース
            published_at_str = snippet["publishedAt"]
            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))

            return VideoInfo(
                video_id=video_id,
                title=snippet["title"],
                url=f"https://www.youtube.com/watch?v={video_id}",
                channel_name=snippet["channelTitle"],
                channel_id=snippet["channelId"],
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                comment_count=int(statistics.get("commentCount", 0)),
                published_at=published_at,
                duration_seconds=duration_seconds,
                is_short=is_short,
                description=snippet.get("description", ""),
                tags=snippet.get("tags", []),
                thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            )

        except Exception as e:
            logger.warning(f"動画情報のパースに失敗: {e}")
            return None

    def _filter_videos(self, videos: List[VideoInfo], criteria: SearchCriteria) -> List[VideoInfo]:
        """
        動画リストをフィルタリング

        Args:
            videos: 動画情報リスト
            criteria: 検索条件

        Returns:
            List[VideoInfo]: フィルタリング後の動画情報リスト
        """
        filtered = []

        for video in videos:
            # 再生回数フィルタ
            if criteria.min_view_count is not None and video.view_count < criteria.min_view_count:
                continue
            if criteria.max_view_count is not None and video.view_count > criteria.max_view_count:
                continue

            # 動画タイプフィルタ
            if criteria.video_type == VideoType.SHORT and not video.is_short:
                continue
            if criteria.video_type == VideoType.NORMAL and video.is_short:
                continue

            filtered.append(video)

        return filtered

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
        try:
            response = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()

            items = response.get("items", [])
            if not items:
                logger.warning(f"動画ID {video_id} が見つかりませんでした")
                return None

            return self._parse_video_item(items[0])

        except HttpError as e:
            logger.error(f"YouTube API呼び出しエラー: {e}", exc_info=True)
            raise YouTubeAPIError(f"YouTube API呼び出しエラー: {e}")
