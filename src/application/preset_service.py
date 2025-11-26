"""
プリセット管理サービス

検索条件のプリセットを保存・読込・削除する
"""
import sqlite3
import os
from typing import List, Optional
from datetime import datetime

from src.domain.models import SearchCriteria, SearchPreset
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PresetService:
    """
    プリセット管理サービス

    検索条件のプリセットをデータベースで管理する
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

        logger.info("PresetServiceを初期化しました")

    def save_preset(self, name: str, criteria: SearchCriteria) -> SearchPreset:
        """
        プリセットを保存

        Args:
            name: プリセット名
            criteria: 検索条件

        Returns:
            SearchPreset: 保存されたプリセット

        Raises:
            ValueError: プリセット名が空、または既に存在する場合
        """
        if not name or not name.strip():
            raise ValueError("プリセット名を入力してください")

        name = name.strip()

        # バリデーション
        criteria.validate()

        logger.info(f"プリセットを保存: {name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().isoformat()

            # 既存のプリセットを確認
            cursor.execute("SELECT id FROM search_presets WHERE name = ?", (name,))
            existing = cursor.fetchone()

            if existing:
                # 更新
                cursor.execute("""
                    UPDATE search_presets
                    SET keyword = ?,
                        min_view_count = ?,
                        max_view_count = ?,
                        video_type = ?,
                        published_after = ?,
                        published_before = ?,
                        max_results = ?,
                        sort_order = ?,
                        updated_at = ?
                    WHERE name = ?
                """, (
                    criteria.keyword,
                    criteria.min_view_count,
                    criteria.max_view_count,
                    criteria.video_type.value if criteria.video_type else None,
                    criteria.published_after.isoformat() if criteria.published_after else None,
                    criteria.published_before.isoformat() if criteria.published_before else None,
                    criteria.max_results,
                    criteria.order,
                    now,
                    name
                ))
                preset_id = existing[0]
                logger.info(f"既存のプリセットを更新しました: {name}")
            else:
                # 新規作成
                cursor.execute("""
                    INSERT INTO search_presets (
                        name, keyword, min_view_count, max_view_count,
                        video_type, published_after, published_before,
                        max_results, sort_order, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    criteria.keyword,
                    criteria.min_view_count,
                    criteria.max_view_count,
                    criteria.video_type.value if criteria.video_type else None,
                    criteria.published_after.isoformat() if criteria.published_after else None,
                    criteria.published_before.isoformat() if criteria.published_before else None,
                    criteria.max_results,
                    criteria.order,
                    now,
                    now
                ))
                preset_id = cursor.lastrowid
                logger.info(f"新しいプリセットを作成しました: {name}")

            conn.commit()
            conn.close()

            # SearchPresetオブジェクトを作成
            preset = SearchPreset(
                preset_id=preset_id,
                name=name,
                criteria=criteria,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now)
            )

            return preset

        except Exception as e:
            logger.error(f"プリセット保存エラー: {e}", exc_info=True)
            raise

    def load_preset(self, name: str) -> Optional[SearchPreset]:
        """
        プリセットを読み込む

        Args:
            name: プリセット名

        Returns:
            Optional[SearchPreset]: プリセット（存在しない場合はNone）
        """
        logger.info(f"プリセットを読み込み: {name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, keyword, min_view_count, max_view_count,
                       video_type, published_after, published_before,
                       max_results, sort_order, created_at, updated_at
                FROM search_presets
                WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                logger.warning(f"プリセットが見つかりません: {name}")
                return None

            preset = self._row_to_preset(row)
            logger.info(f"プリセットを読み込みました: {name}")
            return preset

        except Exception as e:
            logger.error(f"プリセット読み込みエラー: {e}", exc_info=True)
            raise

    def list_presets(self) -> List[SearchPreset]:
        """
        すべてのプリセットを取得

        Returns:
            List[SearchPreset]: プリセットのリスト
        """
        logger.info("プリセット一覧を取得")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, keyword, min_view_count, max_view_count,
                       video_type, published_after, published_before,
                       max_results, sort_order, created_at, updated_at
                FROM search_presets
                ORDER BY updated_at DESC
            """)

            rows = cursor.fetchall()
            conn.close()

            presets = [self._row_to_preset(row) for row in rows]
            logger.info(f"{len(presets)}件のプリセットを取得しました")

            return presets

        except Exception as e:
            logger.error(f"プリセット一覧取得エラー: {e}", exc_info=True)
            raise

    def delete_preset(self, name: str) -> bool:
        """
        プリセットを削除

        Args:
            name: プリセット名

        Returns:
            bool: 削除に成功した場合True、プリセットが存在しない場合False
        """
        logger.info(f"プリセットを削除: {name}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM search_presets WHERE name = ?", (name,))
            deleted_count = cursor.rowcount

            conn.commit()
            conn.close()

            if deleted_count > 0:
                logger.info(f"プリセットを削除しました: {name}")
                return True
            else:
                logger.warning(f"プリセットが見つかりません: {name}")
                return False

        except Exception as e:
            logger.error(f"プリセット削除エラー: {e}", exc_info=True)
            raise

    def _row_to_preset(self, row: tuple) -> SearchPreset:
        """
        データベース行をSearchPresetオブジェクトに変換

        Args:
            row: データベース行

        Returns:
            SearchPreset: プリセットオブジェクト
        """
        from src.domain.models import VideoType

        preset_id, name, keyword, min_view, max_view, video_type, \
            pub_after, pub_before, max_results, sort_order, created_at, updated_at = row

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

        # SearchPresetを作成
        preset = SearchPreset(
            preset_id=preset_id,
            name=name,
            criteria=criteria,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at)
        )

        return preset
