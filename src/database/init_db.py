"""
データベース初期化

SQLiteデータベースのテーブルを作成する
"""
import sqlite3
import os
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseInitializer:
    """
    データベース初期化クラス

    SQLiteデータベースのテーブルを作成・初期化する
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        初期化

        Args:
            db_path: データベースファイルパス
                    指定しない場合は環境変数DATABASE_PATHまたはデフォルトパスを使用
        """
        self.db_path = db_path or os.getenv("DATABASE_PATH", "youtube_analyzer.db")
        logger.info(f"DatabaseInitializerを初期化しました: {self.db_path}")

    def initialize(self) -> None:
        """
        データベースを初期化

        テーブルが存在しない場合は作成する
        """
        logger.info("データベース初期化を開始します")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 検索プリセットテーブル
            self._create_presets_table(cursor)

            # 検索履歴テーブル
            self._create_search_history_table(cursor)

            conn.commit()
            conn.close()

            logger.info("データベース初期化が完了しました")

        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}", exc_info=True)
            raise

    def _create_presets_table(self, cursor: sqlite3.Cursor) -> None:
        """
        検索プリセットテーブルを作成

        Args:
            cursor: データベースカーソル
        """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                keyword TEXT NOT NULL,
                min_view_count INTEGER,
                max_view_count INTEGER,
                video_type TEXT,
                published_after TEXT,
                published_before TEXT,
                max_results INTEGER,
                sort_order TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        logger.info("検索プリセットテーブルを作成しました")

    def _create_search_history_table(self, cursor: sqlite3.Cursor) -> None:
        """
        検索履歴テーブルを作成

        Args:
            cursor: データベースカーソル
        """
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                min_view_count INTEGER,
                max_view_count INTEGER,
                video_type TEXT,
                published_after TEXT,
                published_before TEXT,
                max_results INTEGER,
                sort_order TEXT,
                result_count INTEGER NOT NULL,
                searched_at TEXT NOT NULL
            )
        """)

        # 検索日時のインデックス
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_history_searched_at
            ON search_history(searched_at DESC)
        """)

        logger.info("検索履歴テーブルを作成しました")

    def drop_all_tables(self) -> None:
        """
        すべてのテーブルを削除

        警告: この操作は元に戻せません
        """
        logger.warning("すべてのテーブルを削除します")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS search_presets")
            cursor.execute("DROP TABLE IF EXISTS search_history")

            conn.commit()
            conn.close()

            logger.info("すべてのテーブルを削除しました")

        except Exception as e:
            logger.error(f"テーブル削除エラー: {e}", exc_info=True)
            raise

    def reset_database(self) -> None:
        """
        データベースをリセット

        すべてのテーブルを削除してから再作成する
        """
        logger.warning("データベースをリセットします")
        self.drop_all_tables()
        self.initialize()
        logger.info("データベースリセットが完了しました")


def main():
    """
    コマンドラインから実行する場合のメイン関数
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # リセットモード
        initializer = DatabaseInitializer()
        initializer.reset_database()
        print("データベースをリセットしました")
    else:
        # 通常の初期化
        initializer = DatabaseInitializer()
        initializer.initialize()
        print("データベースを初期化しました")


if __name__ == "__main__":
    main()
