"""
検索履歴パネル

過去の検索履歴を表示するUIコンポーネント
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from datetime import datetime

from src.domain.models import SearchCriteria, SearchHistory
from src.application.history_service import HistoryService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryPanel(tk.Toplevel):
    """
    検索履歴パネル（別ウィンドウ）

    過去の検索履歴を表示し、履歴から再検索できる
    """

    def __init__(self, parent, on_search_callback: Optional[Callable[[SearchCriteria], None]] = None):
        """
        初期化

        Args:
            parent: 親ウィンドウ
            on_search_callback: 履歴から再検索する時のコールバック関数
        """
        super().__init__(parent)
        self.title("検索履歴")
        self.geometry("800x500")

        self.on_search_callback = on_search_callback
        self.history_service = HistoryService()

        self._create_widgets()
        self._load_history()

        logger.info("HistoryPanelを初期化しました")

    def _create_widgets(self):
        """ウィジェットを作成"""
        # ツールバー
        toolbar = ttk.Frame(self, padding="10")
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(
            toolbar,
            text="更新",
            command=self._load_history,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            toolbar,
            text="すべてクリア",
            command=self._clear_all_history,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        self.history_label = ttk.Label(
            toolbar,
            text="履歴: 0件",
            font=('', 9)
        )
        self.history_label.pack(side=tk.RIGHT, padx=5)

        # Treeview（履歴テーブル）
        tree_frame = ttk.Frame(self, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # スクロールバー
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ('searched_at', 'keyword', 'result_count', 'conditions')

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=y_scrollbar.set
        )

        y_scrollbar.config(command=self.tree.yview)

        # カラムの設定
        self.tree.heading('searched_at', text='検索日時')
        self.tree.heading('keyword', text='キーワード')
        self.tree.heading('result_count', text='結果件数')
        self.tree.heading('conditions', text='条件')

        self.tree.column('searched_at', width=150, minwidth=120)
        self.tree.column('keyword', width=200, minwidth=150)
        self.tree.column('result_count', width=80, minwidth=60, anchor=tk.E)
        self.tree.column('conditions', width=300, minwidth=200)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # ダブルクリックで再検索
        self.tree.bind('<Double-1>', self._on_double_click)

        # ボタンパネル
        button_panel = ttk.Frame(self, padding="10")
        button_panel.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(
            button_panel,
            text="この条件で再検索",
            command=self._research_selected,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_panel,
            text="削除",
            command=self._delete_selected,
            width=10
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_panel,
            text="閉じる",
            command=self.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=5)

    def _load_history(self):
        """検索履歴を読み込んで表示"""
        try:
            # 既存のアイテムをクリア
            for item in self.tree.get_children():
                self.tree.delete(item)

            # 最近の履歴を取得
            histories = self.history_service.get_recent_history(limit=100)

            # 履歴を表示
            for history in histories:
                searched_at_str = history.executed_at.strftime('%Y-%m-%d %H:%M:%S')
                keyword = history.criteria.keyword
                result_count = history.result_count

                # 条件の概要
                conditions = []
                if history.criteria.min_view_count:
                    conditions.append(f"再生≥{history.criteria.min_view_count:,}")
                if history.criteria.max_view_count:
                    conditions.append(f"再生≤{history.criteria.max_view_count:,}")
                if history.criteria.video_type:
                    type_str = {
                        'SHORT': 'ショート',
                        'NORMAL': '通常',
                        'ALL': 'すべて'
                    }.get(history.criteria.video_type.value, '')
                    if type_str and type_str != 'すべて':
                        conditions.append(type_str)

                conditions_str = ", ".join(conditions) if conditions else "条件なし"

                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        searched_at_str,
                        keyword,
                        f"{result_count}件",
                        conditions_str
                    ),
                    tags=(history.history_id,)
                )

            # 履歴件数を更新
            self.history_label.config(text=f"履歴: {len(histories)}件")

            logger.info(f"{len(histories)}件の検索履歴を表示しました")

        except Exception as e:
            logger.error(f"検索履歴の読み込みエラー: {e}", exc_info=True)
            messagebox.showerror("エラー", f"検索履歴の読み込みに失敗しました:\n{e}")

    def _get_selected_history(self) -> Optional[SearchHistory]:
        """選択されている履歴を取得"""
        item = self.tree.selection()
        if not item:
            return None

        tags = self.tree.item(item[0], 'tags')
        if not tags:
            return None

        history_id = int(tags[0])
        return self.history_service.get_history_by_id(history_id)

    def _on_double_click(self, event):
        """アイテムがダブルクリックされた時の処理"""
        self._research_selected()

    def _research_selected(self):
        """選択した履歴で再検索"""
        history = self._get_selected_history()
        if not history:
            messagebox.showwarning("再検索", "再検索する履歴を選択してください")
            return

        if self.on_search_callback:
            logger.info(f"履歴から再検索: {history.criteria.keyword}")
            self.on_search_callback(history.criteria)
            self.destroy()  # ウィンドウを閉じる
        else:
            messagebox.showinfo("再検索", "再検索機能は利用できません")

    def _delete_selected(self):
        """選択した履歴を削除"""
        history = self._get_selected_history()
        if not history:
            messagebox.showwarning("削除", "削除する履歴を選択してください")
            return

        # 確認ダイアログ
        result = messagebox.askyesno(
            "削除確認",
            f"検索履歴を削除してもよろしいですか？\n\nキーワード: {history.criteria.keyword}\n検索日時: {history.executed_at}"
        )

        if not result:
            return

        try:
            deleted = self.history_service.delete_history(history.history_id)
            if deleted:
                self._load_history()  # 再読み込み
                logger.info(f"検索履歴を削除しました: ID={history.history_id}")
                messagebox.showinfo("削除完了", "検索履歴を削除しました")
            else:
                messagebox.showerror("削除失敗", "検索履歴が見つかりません")

        except Exception as e:
            logger.error(f"検索履歴の削除エラー: {e}", exc_info=True)
            messagebox.showerror("エラー", f"検索履歴の削除に失敗しました:\n{e}")

    def _clear_all_history(self):
        """すべての履歴をクリア"""
        # 確認ダイアログ
        result = messagebox.askyesno(
            "全削除確認",
            "すべての検索履歴を削除してもよろしいですか？\n\nこの操作は元に戻せません。",
            icon='warning'
        )

        if not result:
            return

        try:
            count = self.history_service.clear_all_history()
            self._load_history()  # 再読み込み
            logger.info(f"{count}件の検索履歴を削除しました")
            messagebox.showinfo("全削除完了", f"{count}件の検索履歴を削除しました")

        except Exception as e:
            logger.error(f"検索履歴の全削除エラー: {e}", exc_info=True)
            messagebox.showerror("エラー", f"検索履歴の削除に失敗しました:\n{e}")
