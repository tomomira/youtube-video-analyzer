"""
Google Sheets エクスポート機能

動画情報をGoogle Spreadsheetsに出力する
"""
import os
from typing import List, Optional
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

from src.domain.models import VideoInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SheetsExporter:
    """
    Google Spreadsheetsにエクスポートするクラス

    動画情報をGoogle Spreadsheetsに出力する
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        初期化

        Args:
            credentials_path: Google API認証情報のJSONファイルパス
                            指定しない場合は環境変数GOOGLE_CREDENTIALS_PATHを使用

        Raises:
            ImportError: gspreadがインストールされていない場合
            ValueError: 認証情報ファイルが見つからない場合
        """
        if not GSPREAD_AVAILABLE:
            raise ImportError(
                "gspreadがインストールされていません。\n"
                "pip install gspread google-auth を実行してください。"
            )

        # 認証情報パスを取得
        self.credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")

        if not self.credentials_path:
            raise ValueError(
                "Google API認証情報が設定されていません。\n"
                ".envファイルにGOOGLE_CREDENTIALS_PATHを設定するか、\n"
                "credentials_pathを指定してください。"
            )

        if not os.path.exists(self.credentials_path):
            raise ValueError(f"認証情報ファイルが見つかりません: {self.credentials_path}")

        # Google Sheets APIクライアントを初期化
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )
            self.client = gspread.authorize(creds)
            logger.info("SheetsExporterを初期化しました")
        except Exception as e:
            logger.error(f"Google Sheets APIクライアントの初期化に失敗: {e}", exc_info=True)
            raise

    def export(self, videos: List[VideoInfo], spreadsheet_name: str,
               worksheet_name: str = "YouTube動画リスト") -> str:
        """
        動画情報をGoogle Spreadsheetsにエクスポート

        Args:
            videos: エクスポートする動画情報リスト
            spreadsheet_name: スプレッドシート名
            worksheet_name: ワークシート名（デフォルト: "YouTube動画リスト"）

        Returns:
            str: スプレッドシートのURL

        Raises:
            ValueError: videosが空の場合
            Exception: API呼び出しに失敗した場合
        """
        if not videos:
            raise ValueError("エクスポートする動画が指定されていません")

        logger.info(
            f"Google Sheetsエクスポート開始: {len(videos)}件の動画を "
            f"{spreadsheet_name}/{worksheet_name} に出力"
        )

        try:
            # スプレッドシートを作成または取得
            spreadsheet = self._get_or_create_spreadsheet(spreadsheet_name)

            # ワークシートを作成または取得
            worksheet = self._get_or_create_worksheet(spreadsheet, worksheet_name)

            # 既存のデータをクリア
            worksheet.clear()

            # ヘッダー行を作成
            headers = self._create_headers()

            # データ行を作成
            data_rows = [self._create_video_row(idx, video)
                        for idx, video in enumerate(videos, start=1)]

            # すべてのデータを一括で書き込み（効率化）
            all_data = [headers] + data_rows
            worksheet.update('A1', all_data)

            # ヘッダー行のフォーマット設定
            self._format_header(worksheet)

            # カラム幅を調整
            self._adjust_column_widths(worksheet)

            spreadsheet_url = spreadsheet.url
            logger.info(f"Google Sheetsエクスポート完了: {spreadsheet_url}")

            return spreadsheet_url

        except Exception as e:
            logger.error(f"Google Sheetsエクスポートエラー: {e}", exc_info=True)
            raise Exception(f"Google Sheetsへの書き込みに失敗しました: {e}")

    def _get_or_create_spreadsheet(self, spreadsheet_name: str):
        """
        スプレッドシートを取得または作成

        Args:
            spreadsheet_name: スプレッドシート名

        Returns:
            スプレッドシートオブジェクト
        """
        try:
            # 既存のスプレッドシートを検索
            spreadsheet = self.client.open(spreadsheet_name)
            logger.info(f"既存のスプレッドシートを開きました: {spreadsheet_name}")
        except gspread.SpreadsheetNotFound:
            # 新規作成
            spreadsheet = self.client.create(spreadsheet_name)
            logger.info(f"新しいスプレッドシートを作成しました: {spreadsheet_name}")

        return spreadsheet

    def _get_or_create_worksheet(self, spreadsheet, worksheet_name: str):
        """
        ワークシートを取得または作成

        Args:
            spreadsheet: スプレッドシートオブジェクト
            worksheet_name: ワークシート名

        Returns:
            ワークシートオブジェクト
        """
        try:
            worksheet = spreadsheet.worksheet(worksheet_name)
            logger.info(f"既存のワークシートを開きました: {worksheet_name}")
        except gspread.WorksheetNotFound:
            # 新規作成
            worksheet = spreadsheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=20
            )
            logger.info(f"新しいワークシートを作成しました: {worksheet_name}")

        return worksheet

    def _create_headers(self) -> List[str]:
        """
        ヘッダー行を作成

        Returns:
            List[str]: ヘッダーのリスト
        """
        return [
            "No",
            "タイトル",
            "URL",
            "チャンネル名",
            "チャンネルID",
            "再生回数",
            "いいね数",
            "コメント数",
            "公開日",
            "動画の長さ",
            "種類",
            "概要",
            "タグ",
            "サムネイルURL"
        ]

    def _create_video_row(self, idx: int, video: VideoInfo) -> List[str]:
        """
        動画情報の行を作成

        Args:
            idx: 行番号
            video: 動画情報

        Returns:
            List[str]: 動画情報の行データ
        """
        # タグをカンマ区切りに変換
        tags_str = ", ".join(video.tags) if video.tags else ""

        # 種類
        video_type = "ショート" if video.is_short else "通常"

        # 公開日をフォーマット
        published_str = video.published_at.strftime('%Y-%m-%d')

        return [
            str(idx),
            video.title,
            video.url,
            video.channel_name,
            video.channel_id,
            str(video.view_count),
            str(video.like_count),
            str(video.comment_count),
            published_str,
            video.duration_formatted,
            video_type,
            video.description,
            tags_str,
            video.thumbnail_url
        ]

    def _format_header(self, worksheet) -> None:
        """
        ヘッダー行のフォーマット設定

        Args:
            worksheet: ワークシートオブジェクト
        """
        try:
            # ヘッダー行を太字に
            worksheet.format('A1:N1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.27, 'green': 0.45, 'blue': 0.77},
                'horizontalAlignment': 'CENTER',
                'textFormat': {'foregroundColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
            })
        except Exception as e:
            logger.warning(f"ヘッダーフォーマット設定に失敗: {e}")

    def _adjust_column_widths(self, worksheet) -> None:
        """
        カラム幅を調整

        Args:
            worksheet: ワークシートオブジェクト
        """
        try:
            # カラム幅の設定
            column_widths = {
                'A': 50,   # No
                'B': 400,  # タイトル
                'C': 300,  # URL
                'D': 150,  # チャンネル名
                'E': 200,  # チャンネルID
                'F': 100,  # 再生回数
                'G': 100,  # いいね数
                'H': 100,  # コメント数
                'I': 100,  # 公開日
                'J': 100,  # 動画の長さ
                'K': 80,   # 種類
                'L': 400,  # 概要
                'M': 200,  # タグ
                'N': 300,  # サムネイルURL
            }

            requests = []
            for col, width in column_widths.items():
                col_idx = ord(col) - ord('A')
                requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': worksheet.id,
                            'dimension': 'COLUMNS',
                            'startIndex': col_idx,
                            'endIndex': col_idx + 1
                        },
                        'properties': {'pixelSize': width},
                        'fields': 'pixelSize'
                    }
                })

            worksheet.spreadsheet.batch_update({'requests': requests})

        except Exception as e:
            logger.warning(f"カラム幅調整に失敗: {e}")
