"""
検索履歴サービス

検索履歴を記録・取得する
"""
import sqlite3
import os
from typing import List, Optional
from datetime import datetime

from src.domain.models import SearchCriteria, SearchHistory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryService:
    """
    検索履歴サービス

    検索履歴をデータベースで管理する
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        初期化

        Args:
            db_path: データベースファイルパス
                    指定しない場合は環境変数DATABASE_PATHまたはデフォルトパスを使用
        """
        self.db_path = db_path or os.getenv("DATABASE_PATH", "youtube_analyzer.db")

        # データベースを初期化（テーブルが存在しない場合も対応）
        from src.database.init_db import DatabaseInitializer
        initializer = DatabaseInitializer(self.db_path)
        initializer.initialize()

        logger.info("HistoryServiceを初期化しました")

    def add_history(self, criteria: SearchCriteria, result_count: int) -> SearchHistory:
        """
        検索履歴を追加

        Args:
            criteria: 検索条件
            result_count: 検索結果件数

        Returns:
            SearchHistory: 追加された検索履歴
        """
        logger.info(f"検索履歴を追加: {criteria.keyword}, 結果件数={result_count}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now()

            cursor.execute("""
                INSERT INTO search_history (
                    keyword, min_view_count, max_view_count,
                    video_type, published_after, published_before,
                    max_results, sort_order, result_count, searched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                criteria.keyword,
                criteria.min_view_count,
                criteria.max_view_count,
                criteria.video_type.value if criteria.video_type else None,
                criteria.published_after.isoformat() if criteria.published_after else None,
                criteria.published_before.isoformat() if criteria.published_before else None,
                criteria.max_results,
                criteria.order,
                result_count,
                now.isoformat()
            ))

            history_id = cursor.lastrowid

            conn.commit()
            conn.close()

            # SearchHistoryオブジェクトを作成
            history = SearchHistory(
                history_id=history_id,
                criteria=criteria,
                result_count=result_count,
                executed_at=now
            )

            logger.info(f"検索履歴を追加しました: ID={history_id}")
            return history

        except Exception as e:
            logger.error(f"検索履歴追加エラー: {e}", exc_info=True)
            raise

    def get_recent_history(self, limit: int = 50) -> List[SearchHistory]:
        """
        最近の検索履歴を取得

        Args:
            limit: 取得件数（デフォルト: 50）

        Returns:
            List[SearchHistory]: 検索履歴のリスト（新しい順）
        """
        logger.info(f"最近の検索履歴を取得: 上限={limit}件")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, keyword, min_view_count, max_view_count,
                       video_type, published_after, published_before,
                       max_results, sort_order, result_count, searched_at
                FROM search_history
                ORDER BY searched_at DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            histories = [self._row_to_history(row) for row in rows]
            logger.info(f"{len(histories)}件の検索履歴を取得しました")

            return histories

        except Exception as e:
            logger.error(f"検索履歴取得エラー: {e}", exc_info=True)
            raise

    def search_history(self, keyword: str, limit: int = 50) -> List[SearchHistory]:
        """
        キーワードで検索履歴を検索

        Args:
            keyword: 検索キーワード
            limit: 取得件数（デフォルト: 50）

        Returns:
            List[SearchHistory]: 検索履歴のリスト（新しい順）
        """
        logger.info(f"検索履歴を検索: キーワード={keyword}, 上限={limit}件")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, keyword, min_view_count, max_view_count,
                       video_type, published_after, published_before,
                       max_results, sort_order, result_count, searched_at
                FROM search_history
                WHERE keyword LIKE ?
                ORDER BY searched_at DESC
                LIMIT ?
            """, (f"%{keyword}%", limit))

            rows = cursor.fetchall()
            conn.close()

            histories = [self._row_to_history(row) for row in rows]
            logger.info(f"{len(histories)}件の検索履歴を取得しました")

            return histories

        except Exception as e:
            logger.error(f"検索履歴検索エラー: {e}", exc_info=True)
            raise

    def get_history_by_id(self, history_id: int) -> Optional[SearchHistory]:
        """
        IDで検索履歴を取得

        Args:
            history_id: 検索履歴ID

        Returns:
            Optional[SearchHistory]: 検索履歴（存在しない場合はNone）
        """
        logger.info(f"検索履歴を取得: ID={history_id}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, keyword, min_view_count, max_view_count,
                       video_type, published_after, published_before,
                       max_results, sort_order, result_count, searched_at
                FROM search_history
                WHERE id = ?
            """, (history_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.warning(f"検索履歴が見つかりません: ID={history_id}")
                return None

            history = self._row_to_history(row)
            logger.info(f"検索履歴を取得しました: ID={history_id}")
            return history

        except Exception as e:
            logger.error(f"検索履歴取得エラー: {e}", exc_info=True)
            raise

    def delete_history(self, history_id: int) -> bool:
        """
        検索履歴を削除

        Args:
            history_id: 検索履歴ID

        Returns:
            bool: 削除に成功した場合True、履歴が存在しない場合False
        """
        logger.info(f"検索履歴を削除: ID={history_id}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"検索履歴を削除しました: ID={history_id}")
                return True
            else:
                logger.warning(f"検索履歴が見つかりません: ID={history_id}")
                return False

        except Exception as e:
            logger.error(f"検索履歴削除エラー: {e}", exc_info=True)
            raise

    def clear_all_history(self) -> int:
        """
        すべての検索履歴を削除

        Returns:
            int: 削除した件数
        """
        logger.warning("すべての検索履歴を削除します")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM search_history")
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            logger.info(f"{deleted_count}件の検索履歴を削除しました")
            return deleted_count

        except Exception as e:
            logger.error(f"検索履歴削除エラー: {e}", exc_info=True)
            raise

    def _row_to_history(self, row: tuple) -> SearchHistory:
        """
        データベース行をSearchHistoryオブジェクトに変換

        Args:
            row: データベース行

        Returns:
            SearchHistory: 検索履歴オブジェクト
        """
        from src.domain.models import VideoType

        history_id, keyword, min_view, max_view, video_type, \
            pub_after, pub_before, max_results, sort_order, result_count, searched_at = row

        # SearchCriteriaを作成
        criteria = SearchCriteria(
            keyword=keyword,
            min_view_count=min_view,
            max_view_count=max_view,
            video_type=VideoType(video_type) if video_type else None,
            published_after=datetime.fromisoformat(pub_after) if pub_after else None,
            published_before=datetime.fromisoformat(pub_before) if pub_before else None,
            max_results=max_results,
            order=sort_order
        )

        # SearchHistoryを作成
        history = SearchHistory(
            history_id=history_id,
            criteria=criteria,
            result_count=result_count,
            executed_at=datetime.fromisoformat(searched_at)
        )

        return history
