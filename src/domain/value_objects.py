"""
値オブジェクト

不変な値を表現するクラス群
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ViewCountRange:
    """
    再生回数範囲

    Attributes:
        min_count: 最小再生回数
        max_count: 最大再生回数
    """
    min_count: Optional[int] = None
    max_count: Optional[int] = None

    def __post_init__(self):
        """バリデーション"""
        if self.min_count is not None and self.min_count < 0:
            raise ValueError("最小再生回数は0以上を指定してください")

        if self.max_count is not None and self.max_count < 0:
            raise ValueError("最大再生回数は0以上を指定してください")

        if (self.min_count is not None and
            self.max_count is not None and
            self.min_count > self.max_count):
            raise ValueError("最小再生回数は最大再生回数以下を指定してください")

    def contains(self, view_count: int) -> bool:
        """
        指定された再生回数が範囲内かチェック

        Args:
            view_count: 再生回数

        Returns:
            bool: 範囲内ならTrue
        """
        if self.min_count is not None and view_count < self.min_count:
            return False
        if self.max_count is not None and view_count > self.max_count:
            return False
        return True


@dataclass(frozen=True)
class YouTubeVideoId:
    """
    YouTube動画ID

    11文字の英数字とアンダースコア、ハイフンからなる文字列

    Attributes:
        value: 動画ID文字列
    """
    value: str

    def __post_init__(self):
        """バリデーション"""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("動画IDは文字列である必要があります")

        if len(self.value) != 11:
            raise ValueError("動画IDは11文字である必要があります")

        # YouTube動画IDの有効文字チェック（英数字、アンダースコア、ハイフン）
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
        if not all(c in valid_chars for c in self.value):
            raise ValueError("動画IDに無効な文字が含まれています")

    def to_url(self) -> str:
        """
        動画URLを生成

        Returns:
            str: YouTube動画URL
        """
        return f"https://www.youtube.com/watch?v={self.value}"


@dataclass(frozen=True)
class ChannelId:
    """
    YouTubeチャンネルID

    Attributes:
        value: チャンネルID文字列
    """
    value: str

    def __post_init__(self):
        """バリデーション"""
        if not self.value or not isinstance(self.value, str):
            raise ValueError("チャンネルIDは文字列である必要があります")

        # チャンネルIDは通常24文字で "UC" で始まる
        if not self.value.startswith("UC") or len(self.value) != 24:
            raise ValueError("チャンネルIDの形式が正しくありません")

    def to_url(self) -> str:
        """
        チャンネルURLを生成

        Returns:
            str: YouTubeチャンネルURL
        """
        return f"https://www.youtube.com/channel/{self.value}"
