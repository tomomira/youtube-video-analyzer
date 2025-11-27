"""
メインウィンドウ

アプリケーションのメインウィンドウ
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List

from src.ui.search_panel import SearchPanel
from src.ui.result_panel import ResultPanel
from src.ui.history_panel import HistoryPanel
from src.domain.models import SearchCriteria, VideoInfo
from src.application.video_search_service import VideoSearchService
from src.application.history_service import HistoryService
from src.infrastructure.excel_exporter import ExcelExporter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """
    メインウィンドウクラス

    アプリケーションのメインウィンドウを管理する
    """

    def __init__(self, root: tk.Tk):
        """
        初期化

        Args:
            root: Tkのルートウィンドウ
        """
        self.root = root
        self.root.title("YouTube Video Analyzer")
        self.root.geometry("1000x700")

        # サービス初期化
        try:
            self.video_search_service = VideoSearchService()
            self.history_service = HistoryService()
            self.excel_exporter = ExcelExporter()
            logger.info("サービスを初期化しました")
        except Exception as e:
            logger.error(f"サービスの初期化に失敗: {e}", exc_info=True)
            messagebox.showerror(
                "初期化エラー",
                f"アプリケーションの初期化に失敗しました:\n{e}\n\n.envファイルにYOUTUBE_API_KEYが設定されているか確認してください。"
            )
            self.root.destroy()
            return

        self._create_menu()
        self._create_widgets()
        self._create_statusbar()

        logger.info("MainWindowを初期化しました")

    def _create_menu(self):
        """メニューバーを作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="Excelにエクスポート", command=self._export_to_excel)
        file_menu.add_command(label="Google Sheetsにエクスポート", command=self._export_to_sheets)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.root.quit)

        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="検索履歴", command=self._show_history)

        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="バージョン情報", command=self._show_about)

    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインコンテナ
        main_container = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 検索条件パネル
        self.search_panel = SearchPanel(
            main_container,
            on_search_callback=self._on_search
        )
        main_container.add(self.search_panel, weight=0)

        # 区切り線
        ttk.Separator(main_container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # 結果表示パネル
        self.result_panel = ResultPanel(
            main_container,
            on_export_callback=self._on_export
        )
        main_container.add(self.result_panel, weight=1)

    def _create_statusbar(self):
        """ステータスバーを作成"""
        self.statusbar = ttk.Label(
            self.root,
            text="準備完了",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # プログレスバー（初期は非表示）
        self.progress = ttk.Progressbar(
            self.root,
            mode='indeterminate'
        )

    def _on_search(self, criteria: SearchCriteria):
        """
        検索実行

        Args:
            criteria: 検索条件
        """
        # 検索を別スレッドで実行（UIをフリーズさせないため）
        thread = threading.Thread(
            target=self._execute_search,
            args=(criteria,),
            daemon=True
        )
        thread.start()

    def _execute_search(self, criteria: SearchCriteria):
        """
        検索を実行（バックグラウンドスレッド）

        Args:
            criteria: 検索条件
        """
        try:
            # UI更新（メインスレッド）
            self.root.after(0, self._search_started)

            # 検索条件を保存（履歴記録用）
            self._last_search_criteria = criteria

            # 検索実行
            logger.info(f"検索実行: {criteria.keyword}")
            videos = self.video_search_service.search(criteria)

            # UI更新（メインスレッド）
            self.root.after(0, self._search_completed, videos)

        except Exception as e:
            logger.error(f"検索エラー: {e}", exc_info=True)
            self.root.after(0, self._search_error, str(e))

    def _search_started(self):
        """検索開始時のUI更新"""
        self.search_panel.set_enabled(False)
        self.result_panel.clear()
        self.statusbar.config(text="検索中...")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, before=self.statusbar)
        self.progress.start(10)
        logger.info("検索を開始しました")

    def _search_completed(self, videos: List[VideoInfo]):
        """
        検索完了時のUI更新

        Args:
            videos: 検索結果の動画リスト
        """
        self.progress.stop()
        self.progress.pack_forget()
        self.search_panel.set_enabled(True)
        self.result_panel.display_results(videos)
        self.statusbar.config(text=f"検索完了: {len(videos)}件の動画を取得しました")
        logger.info(f"検索完了: {len(videos)}件")

        # 検索履歴に記録（最後に実行した検索条件を保存）
        if hasattr(self, '_last_search_criteria'):
            try:
                self.history_service.add_history(self._last_search_criteria, len(videos))
            except Exception as e:
                logger.warning(f"検索履歴の記録に失敗: {e}")

    def _search_error(self, error_message: str):
        """
        検索エラー時のUI更新

        Args:
            error_message: エラーメッセージ
        """
        self.progress.stop()
        self.progress.pack_forget()
        self.search_panel.set_enabled(True)
        self.statusbar.config(text="検索エラー")

        messagebox.showerror("検索エラー", f"検索中にエラーが発生しました:\n\n{error_message}")
        logger.error(f"検索エラー: {error_message}")

    def _on_export(self, videos: List[VideoInfo]):
        """
        エクスポート処理

        Args:
            videos: エクスポートする動画リスト
        """
        # outputフォルダを作成（存在しない場合）
        import os
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"出力フォルダを作成しました: {output_dir}")

        # デフォルトのファイル名（日時付き）
        from datetime import datetime
        default_filename = f"youtube_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # ファイル保存ダイアログ（outputフォルダをデフォルトに）
        filename = filedialog.asksaveasfilename(
            initialdir=output_dir,
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excelファイル", "*.xlsx"), ("すべてのファイル", "*.*")],
            title="エクスポート先を選択"
        )

        if not filename:
            return

        # エクスポートを別スレッドで実行
        thread = threading.Thread(
            target=self._execute_export,
            args=(videos, filename),
            daemon=True
        )
        thread.start()

    def _execute_export(self, videos: List[VideoInfo], filename: str):
        """
        エクスポートを実行（バックグラウンドスレッド）

        Args:
            videos: エクスポートする動画リスト
            filename: 保存先ファイル名
        """
        try:
            # UI更新
            self.root.after(0, self._export_started)

            # Excelエクスポート実行
            self.excel_exporter.export(videos, filename)

            logger.info(f"エクスポート完了: {filename}")

            # UI更新
            self.root.after(0, self._export_completed, filename)

        except Exception as e:
            logger.error(f"エクスポートエラー: {e}", exc_info=True)
            self.root.after(0, self._export_error, str(e))

    def _export_started(self):
        """エクスポート開始時のUI更新"""
        self.statusbar.config(text="エクスポート中...")
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, before=self.statusbar)
        self.progress.start(10)

    def _export_completed(self, filename: str):
        """
        エクスポート完了時のUI更新

        Args:
            filename: 保存先ファイル名
        """
        self.progress.stop()
        self.progress.pack_forget()
        self.statusbar.config(text=f"エクスポート完了: {filename}")
        messagebox.showinfo("エクスポート完了", f"ファイルに保存しました:\n{filename}")

    def _export_error(self, error_message: str):
        """
        エクスポートエラー時のUI更新

        Args:
            error_message: エラーメッセージ
        """
        self.progress.stop()
        self.progress.pack_forget()
        self.statusbar.config(text="エクスポートエラー")
        messagebox.showerror("エクスポートエラー", f"エクスポート中にエラーが発生しました:\n\n{error_message}")

    def _export_to_excel(self):
        """Excelエクスポート（メニューから）"""
        videos = self.result_panel.videos
        if not videos:
            messagebox.showinfo("エクスポート", "エクスポートする検索結果がありません")
            return

        self._on_export(videos)

    def _export_to_sheets(self):
        """Google Sheetsエクスポート"""
        videos = self.result_panel.videos
        if not videos:
            messagebox.showinfo("エクスポート", "エクスポートする検索結果がありません")
            return

        # スプレッドシート名を入力
        import tkinter.simpledialog as simpledialog
        spreadsheet_name = simpledialog.askstring(
            "Google Sheetsエクスポート",
            "スプレッドシート名を入力してください:",
            parent=self.root,
            initialvalue="YouTube動画リスト"
        )

        if not spreadsheet_name:
            return

        # エクスポートを別スレッドで実行
        thread = threading.Thread(
            target=self._execute_sheets_export,
            args=(videos, spreadsheet_name),
            daemon=True
        )
        thread.start()

    def _execute_sheets_export(self, videos: List[VideoInfo], spreadsheet_name: str):
        """
        Google Sheetsエクスポートを実行（バックグラウンドスレッド）

        Args:
            videos: エクスポートする動画リスト
            spreadsheet_name: スプレッドシート名
        """
        try:
            # UI更新
            self.root.after(0, self._export_started)

            # SheetsExporterをインポート
            try:
                from src.infrastructure.sheets_exporter import SheetsExporter
                exporter = SheetsExporter()
            except ImportError as e:
                raise Exception(
                    "Google Sheetsエクスポートに必要なライブラリがインストールされていません。\n"
                    "以下のコマンドを実行してください:\n"
                    "pip install gspread google-auth"
                )
            except ValueError as e:
                raise Exception(
                    "Google API認証情報が設定されていません。\n"
                    ".envファイルにGOOGLE_CREDENTIALS_PATHを設定してください。"
                )

            # エクスポート実行
            url = exporter.export(videos, spreadsheet_name)

            logger.info(f"Google Sheetsエクスポート完了: {url}")

            # UI更新
            self.root.after(0, self._sheets_export_completed, url)

        except Exception as e:
            logger.error(f"Google Sheetsエクスポートエラー: {e}", exc_info=True)
            self.root.after(0, self._export_error, str(e))

    def _sheets_export_completed(self, url: str):
        """
        Google Sheetsエクスポート完了時のUI更新

        Args:
            url: スプレッドシートのURL
        """
        self.progress.stop()
        self.progress.pack_forget()
        self.statusbar.config(text=f"Google Sheetsエクスポート完了")

        # URLをクリップボードにコピー
        self.root.clipboard_clear()
        self.root.clipboard_append(url)

        messagebox.showinfo(
            "Google Sheetsエクスポート完了",
            f"スプレッドシートに保存しました。\n\nURL（クリップボードにコピー済み）:\n{url}"
        )

    def _show_history(self):
        """検索履歴を表示"""
        try:
            history_panel = HistoryPanel(
                self.root,
                on_search_callback=self._on_search_from_history
            )
            logger.info("検索履歴パネルを開きました")
        except Exception as e:
            logger.error(f"検索履歴パネルの表示エラー: {e}", exc_info=True)
            messagebox.showerror("エラー", f"検索履歴パネルの表示に失敗しました:\n{e}")

    def _on_search_from_history(self, criteria: SearchCriteria):
        """
        履歴から再検索

        Args:
            criteria: 検索条件
        """
        # SearchPanelに検索条件を設定
        self.search_panel.set_search_criteria(criteria)

        # 検索実行
        self._on_search(criteria)

    def _show_about(self):
        """バージョン情報を表示"""
        messagebox.showinfo(
            "バージョン情報",
            "YouTube Video Analyzer\n\n"
            "Version: 1.0.0 (Phase 4)\n"
            "YouTube動画を効率的に検索・分析するツール\n\n"
            "Powered by YouTube Data API v3"
        )

    def run(self):
        """アプリケーションを実行"""
        logger.info("アプリケーションを起動しました")
        self.root.mainloop()
