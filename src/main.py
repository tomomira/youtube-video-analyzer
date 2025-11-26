"""
YouTube Video Analyzer

エントリーポイント
"""
import tkinter as tk
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.main_window import MainWindow
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """メイン関数"""
    try:
        # 環境変数の確認
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            import tkinter.messagebox as messagebox
            root = tk.Tk()
            root.withdraw()  # メインウィンドウを隠す
            messagebox.showerror(
                "設定エラー",
                "YouTube API キーが設定されていません。\n\n"
                ".envファイルにYOUTUBE_API_KEYを設定してください。\n"
                "詳細は docs/youtube-api-setup-guide.md を参照してください。"
            )
            root.destroy()
            sys.exit(1)

        # メインウィンドウを作成
        root = tk.Tk()
        app = MainWindow(root)
        app.run()

    except KeyboardInterrupt:
        logger.info("アプリケーションを終了しました（Ctrl+C）")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "エラー",
            f"予期しないエラーが発生しました:\n\n{e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
