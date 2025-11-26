"""
検索条件パネル

ユーザーが検索条件を入力するためのUIコンポーネント
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Callable, Optional

from src.domain.models import SearchCriteria, VideoType
from src.application.preset_service import PresetService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SearchPanel(ttk.Frame):
    """
    検索条件入力パネル

    キーワード、再生回数、動画タイプ、公開日範囲などの検索条件を入力するUI
    """

    def __init__(self, parent, on_search_callback: Callable[[SearchCriteria], None]):
        """
        初期化

        Args:
            parent: 親ウィジェット
            on_search_callback: 検索ボタンがクリックされた時のコールバック関数
        """
        super().__init__(parent, padding="10")
        self.on_search_callback = on_search_callback
        self.preset_service = PresetService()

        self._create_widgets()
        logger.info("SearchPanelを初期化しました")

    def _create_widgets(self):
        """ウィジェットを作成"""
        # プリセット選択
        ttk.Label(self, text="プリセット:").grid(row=0, column=0, sticky=tk.W, pady=5)
        preset_frame = ttk.Frame(self)
        preset_frame.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=5)

        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            width=20,
            state="readonly"
        )
        self.preset_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_selected)

        ttk.Button(
            preset_frame,
            text="読込",
            command=self._load_preset,
            width=8
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            preset_frame,
            text="保存",
            command=self._save_preset,
            width=8
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            preset_frame,
            text="削除",
            command=self._delete_preset,
            width=8
        ).pack(side=tk.LEFT, padx=2)

        # プリセット一覧を読み込み
        self._refresh_preset_list()

        # キーワード入力
        ttk.Label(self, text="検索キーワード:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.keyword_var = tk.StringVar()
        self.keyword_entry = ttk.Entry(self, textvariable=self.keyword_var, width=40)
        self.keyword_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=5)

        # 再生回数範囲
        ttk.Label(self, text="最小再生回数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.min_views_var = tk.StringVar(value="")
        self.min_views_entry = ttk.Entry(self, textvariable=self.min_views_var, width=15)
        self.min_views_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Label(self, text="最大再生回数:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.max_views_var = tk.StringVar(value="")
        self.max_views_entry = ttk.Entry(self, textvariable=self.max_views_var, width=15)
        self.max_views_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        # 動画タイプ選択
        ttk.Label(self, text="動画タイプ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.video_type_var = tk.StringVar(value="all")
        video_type_frame = ttk.Frame(self)
        video_type_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=5)

        ttk.Radiobutton(
            video_type_frame,
            text="すべて",
            variable=self.video_type_var,
            value="all"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            video_type_frame,
            text="ショート動画",
            variable=self.video_type_var,
            value="short"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            video_type_frame,
            text="通常動画",
            variable=self.video_type_var,
            value="normal"
        ).pack(side=tk.LEFT, padx=5)

        # 最大取得件数
        ttk.Label(self, text="最大取得件数:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.max_results_var = tk.StringVar(value="50")
        self.max_results_spinbox = ttk.Spinbox(
            self,
            from_=1,
            to=500,
            textvariable=self.max_results_var,
            width=15
        )
        self.max_results_spinbox.grid(row=5, column=1, sticky=tk.W, pady=5)

        # ソート順
        ttk.Label(self, text="ソート順:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.order_var = tk.StringVar(value="viewCount")
        self.order_combo = ttk.Combobox(
            self,
            textvariable=self.order_var,
            width=15,
            state="readonly"
        )
        self.order_combo['values'] = (
            'viewCount',      # 再生回数順
            'date',           # 日付順
            'rating',         # 評価順
            'relevance',      # 関連性順
            'title',          # タイトル順
        )
        self.order_combo.grid(row=6, column=1, sticky=tk.W, pady=5)

        # 検索ボタン
        self.search_button = ttk.Button(
            self,
            text="検索",
            command=self._on_search_clicked,
            width=20
        )
        self.search_button.grid(row=7, column=0, columnspan=3, pady=20)

        # カラムの伸縮設定
        self.columnconfigure(1, weight=1)

    def _on_search_clicked(self):
        """検索ボタンがクリックされた時の処理"""
        try:
            criteria = self.get_search_criteria()
            logger.info(f"検索開始: キーワード='{criteria.keyword}'")
            self.on_search_callback(criteria)
        except ValueError as e:
            logger.error(f"検索条件エラー: {e}")
            self._show_error(str(e))

    def get_search_criteria(self) -> SearchCriteria:
        """
        入力された検索条件を取得

        Returns:
            SearchCriteria: 検索条件オブジェクト

        Raises:
            ValueError: 入力値が不正な場合
        """
        keyword = self.keyword_var.get().strip()
        if not keyword:
            raise ValueError("検索キーワードを入力してください")

        # 再生回数範囲
        min_views_str = self.min_views_var.get().strip()
        max_views_str = self.max_views_var.get().strip()

        min_view_count = None
        if min_views_str:
            try:
                min_view_count = int(min_views_str)
                if min_view_count < 0:
                    raise ValueError("最小再生回数は0以上を指定してください")
            except ValueError:
                raise ValueError("最小再生回数は数値で入力してください")

        max_view_count = None
        if max_views_str:
            try:
                max_view_count = int(max_views_str)
                if max_view_count < 0:
                    raise ValueError("最大再生回数は0以上を指定してください")
            except ValueError:
                raise ValueError("最大再生回数は数値で入力してください")

        # 動画タイプ
        video_type_str = self.video_type_var.get()
        video_type = VideoType.ALL
        if video_type_str == "short":
            video_type = VideoType.SHORT
        elif video_type_str == "normal":
            video_type = VideoType.NORMAL

        # 最大取得件数
        try:
            max_results = int(self.max_results_var.get())
        except ValueError:
            raise ValueError("最大取得件数は数値で入力してください")

        # ソート順
        order = self.order_var.get()

        criteria = SearchCriteria(
            keyword=keyword,
            min_view_count=min_view_count,
            max_view_count=max_view_count,
            video_type=video_type,
            max_results=max_results,
            order=order
        )

        # バリデーション
        criteria.validate()

        return criteria

    def _show_error(self, message: str):
        """
        エラーメッセージを表示

        Args:
            message: エラーメッセージ
        """
        import tkinter.messagebox as messagebox
        messagebox.showerror("入力エラー", message)

    def set_enabled(self, enabled: bool):
        """
        パネルの有効/無効を切り替え

        Args:
            enabled: Trueで有効、Falseで無効
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        self.keyword_entry.config(state=state)
        self.min_views_entry.config(state=state)
        self.max_views_entry.config(state=state)
        self.max_results_spinbox.config(state=state)
        self.order_combo.config(state='readonly' if enabled else tk.DISABLED)
        self.search_button.config(state=state)

        # ラジオボタンの状態変更
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for radio in child.winfo_children():
                    if isinstance(radio, ttk.Radiobutton):
                        radio.config(state=state)

    def clear(self):
        """入力フィールドをクリア"""
        self.keyword_var.set("")
        self.min_views_var.set("")
        self.max_views_var.set("")
        self.video_type_var.set("all")
        self.max_results_var.set("50")
        self.order_var.set("viewCount")
        logger.info("検索条件をクリアしました")

    def set_search_criteria(self, criteria: SearchCriteria):
        """
        検索条件をUIに設定

        Args:
            criteria: 設定する検索条件
        """
        self.keyword_var.set(criteria.keyword)
        self.min_views_var.set(str(criteria.min_view_count) if criteria.min_view_count else "")
        self.max_views_var.set(str(criteria.max_view_count) if criteria.max_view_count else "")

        # 動画タイプ
        if criteria.video_type == VideoType.SHORT:
            self.video_type_var.set("short")
        elif criteria.video_type == VideoType.NORMAL:
            self.video_type_var.set("normal")
        else:
            self.video_type_var.set("all")

        self.max_results_var.set(str(criteria.max_results))
        self.order_var.set(criteria.order if criteria.order else "viewCount")

        logger.info(f"検索条件を設定しました: {criteria.keyword}")

    def _refresh_preset_list(self):
        """プリセット一覧を更新"""
        try:
            presets = self.preset_service.list_presets()
            preset_names = [preset.name for preset in presets]
            self.preset_combo['values'] = preset_names
            logger.info(f"プリセット一覧を更新しました: {len(preset_names)}件")
        except Exception as e:
            logger.error(f"プリセット一覧の取得に失敗: {e}", exc_info=True)

    def _on_preset_selected(self, event):
        """プリセットが選択された時の処理"""
        # コンボボックスから選択しただけでは読み込まない
        pass

    def _load_preset(self):
        """プリセットを読み込む"""
        preset_name = self.preset_var.get()
        if not preset_name:
            import tkinter.messagebox as messagebox
            messagebox.showwarning("プリセット読込", "読み込むプリセットを選択してください")
            return

        try:
            preset = self.preset_service.load_preset(preset_name)
            if preset:
                self.set_search_criteria(preset.criteria)
                logger.info(f"プリセットを読み込みました: {preset_name}")
                import tkinter.messagebox as messagebox
                messagebox.showinfo("プリセット読込", f"プリセット「{preset_name}」を読み込みました")
            else:
                import tkinter.messagebox as messagebox
                messagebox.showerror("プリセット読込", f"プリセット「{preset_name}」が見つかりません")
        except Exception as e:
            logger.error(f"プリセット読込エラー: {e}", exc_info=True)
            import tkinter.messagebox as messagebox
            messagebox.showerror("プリセット読込", f"プリセットの読み込みに失敗しました:\n{e}")

    def _save_preset(self):
        """プリセットを保存"""
        import tkinter.simpledialog as simpledialog
        import tkinter.messagebox as messagebox

        # プリセット名を入力
        preset_name = simpledialog.askstring(
            "プリセット保存",
            "プリセット名を入力してください:",
            parent=self
        )

        if not preset_name:
            return

        try:
            # 現在の検索条件を取得
            criteria = self.get_search_criteria()

            # プリセットを保存
            self.preset_service.save_preset(preset_name, criteria)

            # プリセット一覧を更新
            self._refresh_preset_list()

            # 保存したプリセットを選択
            self.preset_var.set(preset_name)

            logger.info(f"プリセットを保存しました: {preset_name}")
            messagebox.showinfo("プリセット保存", f"プリセット「{preset_name}」を保存しました")

        except ValueError as e:
            logger.error(f"プリセット保存エラー: {e}")
            messagebox.showerror("プリセット保存", str(e))
        except Exception as e:
            logger.error(f"プリセット保存エラー: {e}", exc_info=True)
            messagebox.showerror("プリセット保存", f"プリセットの保存に失敗しました:\n{e}")

    def _delete_preset(self):
        """プリセットを削除"""
        import tkinter.messagebox as messagebox

        preset_name = self.preset_var.get()
        if not preset_name:
            messagebox.showwarning("プリセット削除", "削除するプリセットを選択してください")
            return

        # 確認ダイアログ
        result = messagebox.askyesno(
            "プリセット削除",
            f"プリセット「{preset_name}」を削除してもよろしいですか？"
        )

        if not result:
            return

        try:
            # プリセットを削除
            deleted = self.preset_service.delete_preset(preset_name)

            if deleted:
                # プリセット一覧を更新
                self._refresh_preset_list()
                self.preset_var.set("")

                logger.info(f"プリセットを削除しました: {preset_name}")
                messagebox.showinfo("プリセット削除", f"プリセット「{preset_name}」を削除しました")
            else:
                messagebox.showerror("プリセット削除", f"プリセット「{preset_name}」が見つかりません")

        except Exception as e:
            logger.error(f"プリセット削除エラー: {e}", exc_info=True)
            messagebox.showerror("プリセット削除", f"プリセットの削除に失敗しました:\n{e}")
