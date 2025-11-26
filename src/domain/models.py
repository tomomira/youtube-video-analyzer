"""
ドメインモデル

YouTube動画情報や検索条件などのドメインオブジェクトを定義
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class VideoType(Enum):
    """動画タイプ"""
    ALL = "all"
    SHORT = "short"
    NORMAL = "normal"


@dataclass
class VideoInfo:
    """
    YouTube動画情報

    Attributes:
        video_id: YouTube動画ID
        title: 動画タイトル
        url: 動画URL
        channel_name: チャンネル名
        channel_id: チャンネルID
        view_count: 再生回数
        like_count: 高評価数
        comment_count: コメント数
        published_at: 公開日時
        duration_seconds: 動画の長さ（秒）
        is_short: ショート動画かどうか
        description: 動画説明文
        tags: タグリスト
        thumbnail_url: サムネイルURL
    """
    video_id: str
    title: str
    url: str
    channel_name: str
    channel_id: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: datetime
    duration_seconds: int
    is_short: bool
    description: str = ""
    tags: List[str] = field(default_factory=list)
    thumbnail_url: str = ""

    @property
    def duration_formatted(self) -> str:
        """
        動画の長さを HH:MM:SS 形式で返す

        Returns:
            str: フォーマットされた動画の長さ
        """
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


@dataclass
class SearchCriteria:
    """
    動画検索条件

    Attributes:
        keyword: 検索キーワード
        min_view_count: 最小再生回数
        max_view_count: 最大再生回数
        video_type: 動画タイプ（all/short/normal）
        published_after: 公開日開始
        published_before: 公開日終了
        max_results: 最大取得件数
        order: ソート順（date/rating/relevance/title/videoCount/viewCount）
        region_code: 地域コード（例: JP）
        language: 言語コード（例: ja）
    """
    keyword: str
    min_view_count: Optional[int] = None
    max_view_count: Optional[int] = None
    video_type: VideoType = VideoType.ALL
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    max_results: int = 50
    order: str = "viewCount"
    region_code: str = "JP"
    language: str = "ja"

    def validate(self) -> None:
        """
        検索条件のバリデーション

        Raises:
            ValueError: バリデーションエラー
        """
        if not self.keyword or not self.keyword.strip():
            raise ValueError("キーワードは必須です")

        if self.max_results <= 0 or self.max_results > 500:
            raise ValueError("最大取得件数は1〜500の範囲で指定してください")

        if self.min_view_count is not None and self.min_view_count < 0:
            raise ValueError("最小再生回数は0以上を指定してください")

        if (self.min_view_count is not None and
            self.max_view_count is not None and
            self.min_view_count > self.max_view_count):
            raise ValueError("最小再生回数は最大再生回数以下を指定してください")

        if (self.published_after is not None and
            self.published_before is not None and
            self.published_after > self.published_before):
            raise ValueError("公開日開始は公開日終了以前を指定してください")

        valid_orders = ["date", "rating", "relevance", "title", "videoCount", "viewCount"]
        if self.order not in valid_orders:
            raise ValueError(f"orderは{valid_orders}のいずれかを指定してください")


@dataclass
class SearchPreset:
    """
    検索条件プリセット

    Attributes:
        preset_id: プリセットID（データベース用）
        name: プリセット名
        criteria: 検索条件
        created_at: 作成日時
        updated_at: 更新日時
    """
    name: str
    criteria: SearchCriteria
    preset_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SearchHistory:
    """
    検索履歴

    Attributes:
        history_id: 履歴ID（データベース用）
        criteria: 検索条件
        result_count: 検索結果件数
        executed_at: 実行日時
    """
    criteria: SearchCriteria
    result_count: int
    history_id: Optional[int] = None
    executed_at: Optional[datetime] = None
