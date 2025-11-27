"""
結果表示パネル

検索結果の動画リストを表示するUIコンポーネント
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional

from src.domain.models import VideoInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResultPanel(ttk.Frame):
    """
    検索結果表示パネル

    動画リストをTreeviewで表示し、ソート機能を提供する
    """

    def __init__(self, parent, on_export_callback: Optional[Callable[[List[VideoInfo]], None]] = None):
        """
        初期化

        Args:
            parent: 親ウィジェット
            on_export_callback: エクスポートボタンがクリックされた時のコールバック関数
        """
        super().__init__(parent, padding="10")
        self.on_export_callback = on_export_callback
        self.videos: List[VideoInfo] = []

        self._create_widgets()
        logger.info("ResultPanelを初期化しました")

    def _create_widgets(self):
        """ウィジェットを作成"""
        # タイトルラベル
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        self.result_label = ttk.Label(
            title_frame,
            text="検索結果: 0件",
            font=('', 10, 'bold')
        )
        self.result_label.pack(side=tk.LEFT)

        # エクスポートボタン
        if self.on_export_callback:
            self.export_button = ttk.Button(
                title_frame,
                text="Excelにエクスポート",
                command=self._on_export_clicked,
                state=tk.DISABLED
            )
            self.export_button.pack(side=tk.RIGHT)

        # Treeviewフレーム（スクロールバー付き）
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # スクロールバー
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview（テーブル表示）
        columns = (
            'title',
            'channel',
            'views',
            'duration',
            'published',
            'type',
            'url'
        )

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        # スクロールバーとTreeviewを連動
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # カラムの設定
        self.tree.heading('title', text='タイトル', command=lambda: self._sort_column('title'))
        self.tree.heading('channel', text='チャンネル', command=lambda: self._sort_column('channel'))
        self.tree.heading('views', text='再生回数', command=lambda: self._sort_column('views'))
        self.tree.heading('duration', text='長さ', command=lambda: self._sort_column('duration'))
        self.tree.heading('published', text='公開日', command=lambda: self._sort_column('published'))
        self.tree.heading('type', text='種類', command=lambda: self._sort_column('type'))
        self.tree.heading('url', text='URL', command=lambda: self._sort_column('url'))

        # カラムの幅設定
        self.tree.column('title', width=300, minwidth=200)
        self.tree.column('channel', width=150, minwidth=100)
        self.tree.column('views', width=100, minwidth=80, anchor=tk.E)
        self.tree.column('duration', width=80, minwidth=60, anchor=tk.E)
        self.tree.column('published', width=100, minwidth=80)
        self.tree.column('type', width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column('url', width=350, minwidth=250)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # ダブルクリックでURLを開く
        self.tree.bind('<Double-1>', self._on_double_click)

        # ソート用の変数
        self._sort_reverse = {}

    def display_results(self, videos: List[VideoInfo]):
        """
        検索結果を表示

        Args:
            videos: 動画情報リスト
        """
        self.videos = videos

        # 既存のアイテムをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 動画情報を追加
        for video in videos:
            # 再生回数をカンマ区切りでフォーマット
            views_formatted = f"{video.view_count:,}"

            # 動画の長さをフォーマット
            duration_formatted = video.duration_formatted

            # 公開日をフォーマット
            published_formatted = video.published_at.strftime('%Y-%m-%d')

            # 動画タイプ
            video_type = "ショート" if video.is_short else "通常"

            self.tree.insert(
                '',
                tk.END,
                values=(
                    video.title,
                    video.channel_name,
                    views_formatted,
                    duration_formatted,
                    published_formatted,
                    video_type,
                    video.url
                ),
                tags=(video.video_id,)
            )

        # 結果件数を更新
        self.result_label.config(text=f"検索結果: {len(videos)}件")

        # エクスポートボタンの有効/無効
        if self.on_export_callback and hasattr(self, 'export_button'):
            state = tk.NORMAL if videos else tk.DISABLED
            self.export_button.config(state=state)

        logger.info(f"{len(videos)}件の検索結果を表示しました")

    def _sort_column(self, col: str):
        """
        カラムでソート

        Args:
            col: カラム名
        """
        # ソート順を切り替え
        reverse = self._sort_reverse.get(col, False)
        self._sort_reverse[col] = not reverse

        # データを取得してソート
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        # 数値カラムの場合は数値としてソート
        if col in ['views', 'duration']:
            # カンマを削除して数値に変換
            data.sort(
                key=lambda x: self._parse_number(x[0]),
                reverse=reverse
            )
        else:
            data.sort(reverse=reverse)

        # ソート後の順序で並び替え
        for index, (_, child) in enumerate(data):
            self.tree.move(child, '', index)

        logger.info(f"カラム '{col}' でソートしました（降順={reverse}）")

    def _parse_number(self, value: str) -> int:
        """
        数値文字列を整数に変換

        Args:
            value: 数値文字列（カンマ区切り可）

        Returns:
            int: 整数値
        """
        try:
            # カンマを削除
            cleaned = value.replace(',', '')
            # 時間形式（HH:MM:SS）の場合は秒数に変換
            if ':' in cleaned:
                parts = cleaned.split(':')
                if len(parts) == 2:  # MM:SS
                    return int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:  # HH:MM:SS
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return int(cleaned)
        except (ValueError, AttributeError):
            return 0

    def _on_double_click(self, event):
        """
        アイテムがダブルクリックされた時の処理

        Args:
            event: イベントオブジェクト
        """
        item = self.tree.selection()
        if not item:
            return

        # 選択されたアイテムのvideo_idを取得
        tags = self.tree.item(item[0], 'tags')
        if not tags:
            return

        video_id = tags[0]

        # 対応する動画を探す
        video = next((v for v in self.videos if v.video_id == video_id), None)
        if video:
            # ブラウザでURLを開く
            import webbrowser
            webbrowser.open(video.url)
            logger.info(f"動画URLを開きました: {video.url}")

    def _on_export_clicked(self):
        """エクスポートボタンがクリックされた時の処理"""
        if self.videos and self.on_export_callback:
            logger.info("エクスポート処理を開始します")
            self.on_export_callback(self.videos)

    def clear(self):
        """表示をクリア"""
        self.videos = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_label.config(text="検索結果: 0件")
        if hasattr(self, 'export_button'):
            self.export_button.config(state=tk.DISABLED)
        logger.info("検索結果をクリアしました")

    def get_selected_video(self) -> Optional[VideoInfo]:
        """
        選択されている動画情報を取得

        Returns:
            Optional[VideoInfo]: 選択されている動画情報（未選択の場合はNone）
        """
        item = self.tree.selection()
        if not item:
            return None

        tags = self.tree.item(item[0], 'tags')
        if not tags:
            return None

        video_id = tags[0]
        return next((v for v in self.videos if v.video_id == video_id), None)
