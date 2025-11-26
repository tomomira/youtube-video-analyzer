"""
統合テスト

各コンポーネント間の連携をテストする
"""
import os
import pytest
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

from src.domain.models import SearchCriteria, VideoInfo, VideoType
from src.application.preset_service import PresetService
from src.application.history_service import HistoryService
from src.infrastructure.excel_exporter import ExcelExporter


class TestPresetIntegration:
    """プリセット機能の統合テスト"""

    def test_preset_save_and_load(self):
        """プリセットの保存と読み込み"""
        # 一時データベースファイル
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = PresetService(db_path)

            # 検索条件を作成
            criteria = SearchCriteria(
                keyword="Python tutorial",
                min_view_count=1000,
                max_view_count=100000,
                video_type=VideoType.NORMAL,
                max_results=50
            )

            # プリセットを保存
            preset = service.save_preset("テストプリセット", criteria)

            assert preset is not None
            assert preset.name == "テストプリセット"
            assert preset.criteria.keyword == "Python tutorial"

            # プリセットを読み込み
            loaded_preset = service.load_preset("テストプリセット")

            assert loaded_preset is not None
            assert loaded_preset.name == "テストプリセット"
            assert loaded_preset.criteria.keyword == "Python tutorial"
            assert loaded_preset.criteria.min_view_count == 1000
            assert loaded_preset.criteria.max_view_count == 100000
            assert loaded_preset.criteria.video_type == VideoType.NORMAL

        finally:
            # クリーンアップ
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_preset_update(self):
        """プリセットの更新"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = PresetService(db_path)

            # 最初の保存
            criteria1 = SearchCriteria(keyword="Python", max_results=50)
            service.save_preset("更新テスト", criteria1)

            # 同じ名前で再保存（更新）
            criteria2 = SearchCriteria(keyword="JavaScript", max_results=100)
            service.save_preset("更新テスト", criteria2)

            # 読み込み
            preset = service.load_preset("更新テスト")

            assert preset.criteria.keyword == "JavaScript"
            assert preset.criteria.max_results == 100

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_preset_delete(self):
        """プリセットの削除"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = PresetService(db_path)

            # プリセットを保存
            criteria = SearchCriteria(keyword="Python", max_results=50)
            service.save_preset("削除テスト", criteria)

            # 削除
            deleted = service.delete_preset("削除テスト")
            assert deleted is True

            # 読み込み（存在しない）
            preset = service.load_preset("削除テスト")
            assert preset is None

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_preset_list(self):
        """プリセット一覧の取得"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = PresetService(db_path)

            # 複数のプリセットを保存
            criteria1 = SearchCriteria(keyword="Python", max_results=50)
            criteria2 = SearchCriteria(keyword="JavaScript", max_results=100)
            criteria3 = SearchCriteria(keyword="Go", max_results=30)

            service.save_preset("プリセット1", criteria1)
            service.save_preset("プリセット2", criteria2)
            service.save_preset("プリセット3", criteria3)

            # 一覧取得
            presets = service.list_presets()

            assert len(presets) == 3
            preset_names = [p.name for p in presets]
            assert "プリセット1" in preset_names
            assert "プリセット2" in preset_names
            assert "プリセット3" in preset_names

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestHistoryIntegration:
    """検索履歴機能の統合テスト"""

    def test_history_add_and_get(self):
        """検索履歴の追加と取得"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = HistoryService(db_path)

            # 検索履歴を追加
            criteria = SearchCriteria(keyword="Python tutorial", max_results=50)
            history = service.add_history(criteria, result_count=42)

            assert history is not None
            assert history.criteria.keyword == "Python tutorial"
            assert history.result_count == 42

            # 履歴を取得
            recent = service.get_recent_history(limit=10)

            assert len(recent) == 1
            assert recent[0].criteria.keyword == "Python tutorial"
            assert recent[0].result_count == 42

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_history_multiple_entries(self):
        """複数の検索履歴"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = HistoryService(db_path)

            # 複数の検索履歴を追加
            service.add_history(SearchCriteria(keyword="Python", max_results=50), 10)
            service.add_history(SearchCriteria(keyword="JavaScript", max_results=50), 20)
            service.add_history(SearchCriteria(keyword="Go", max_results=50), 30)

            # 最近の履歴を取得
            recent = service.get_recent_history(limit=10)

            assert len(recent) == 3
            # 新しい順に並んでいるか確認
            assert recent[0].criteria.keyword == "Go"
            assert recent[1].criteria.keyword == "JavaScript"
            assert recent[2].criteria.keyword == "Python"

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_history_search(self):
        """キーワードで履歴検索"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = HistoryService(db_path)

            # 複数の検索履歴を追加
            service.add_history(SearchCriteria(keyword="Python tutorial", max_results=50), 10)
            service.add_history(SearchCriteria(keyword="JavaScript basics", max_results=50), 20)
            service.add_history(SearchCriteria(keyword="Python advanced", max_results=50), 30)

            # Pythonを含む履歴を検索
            python_history = service.search_history("Python")

            assert len(python_history) == 2
            keywords = [h.criteria.keyword for h in python_history]
            assert "Python tutorial" in keywords
            assert "Python advanced" in keywords

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_history_delete(self):
        """検索履歴の削除"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = HistoryService(db_path)

            # 履歴を追加
            history = service.add_history(SearchCriteria(keyword="Python", max_results=50), 10)

            # 削除
            deleted = service.delete_history(history.history_id)
            assert deleted is True

            # 取得（存在しない）
            retrieved = service.get_history_by_id(history.history_id)
            assert retrieved is None

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_history_clear_all(self):
        """すべての検索履歴をクリア"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        try:
            service = HistoryService(db_path)

            # 複数の履歴を追加
            service.add_history(SearchCriteria(keyword="Python", max_results=50), 10)
            service.add_history(SearchCriteria(keyword="JavaScript", max_results=50), 20)
            service.add_history(SearchCriteria(keyword="Go", max_results=50), 30)

            # すべてクリア
            count = service.clear_all_history()
            assert count == 3

            # 履歴が空になったことを確認
            recent = service.get_recent_history(limit=10)
            assert len(recent) == 0

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestExcelExportIntegration:
    """Excelエクスポート機能の統合テスト"""

    def test_excel_export(self):
        """Excelエクスポート"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
            file_path = f.name

        try:
            exporter = ExcelExporter()

            # ダミーデータ
            videos = [
                VideoInfo(
                    video_id="test1",
                    title="テスト動画1",
                    url="https://www.youtube.com/watch?v=test1",
                    channel_name="テストチャンネル1",
                    channel_id="UC1234567890",
                    view_count=1000,
                    like_count=50,
                    comment_count=10,
                    published_at=datetime(2024, 1, 1),
                    duration_seconds=180,
                    is_short=False
                ),
                VideoInfo(
                    video_id="test2",
                    title="テスト動画2",
                    url="https://www.youtube.com/watch?v=test2",
                    channel_name="テストチャンネル2",
                    channel_id="UC9876543210",
                    view_count=5000,
                    like_count=100,
                    comment_count=20,
                    published_at=datetime(2024, 2, 1),
                    duration_seconds=45,
                    is_short=True
                )
            ]

            # エクスポート
            exporter.export(videos, file_path)

            # ファイルが作成されたことを確認
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

        finally:
            # クリーンアップ
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_excel_export_empty_list(self):
        """空のリストでエクスポート"""
        exporter = ExcelExporter()

        with pytest.raises(ValueError, match="エクスポートする動画が指定されていません"):
            exporter.export([], "test.xlsx")


class TestEndToEndWorkflow:
    """エンドツーエンドのワークフロー統合テスト"""

    def test_search_save_export_workflow(self):
        """検索→保存→エクスポートのワークフロー"""
        # 一時ファイル
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
            excel_path = f.name

        try:
            # 1. 検索条件を作成
            criteria = SearchCriteria(
                keyword="Python tutorial",
                min_view_count=1000,
                video_type=VideoType.NORMAL,
                max_results=10
            )

            # 2. プリセットとして保存
            preset_service = PresetService(db_path)
            preset = preset_service.save_preset("Pythonチュートリアル", criteria)

            assert preset is not None

            # 3. 検索実行（モック）
            mock_videos = [
                VideoInfo(
                    video_id=f"test{i}",
                    title=f"Python Tutorial {i}",
                    url=f"https://www.youtube.com/watch?v=test{i}",
                    channel_name=f"Channel {i}",
                    channel_id=f"UC{i}234567890",
                    view_count=1000 * (i + 1),
                    like_count=50 * (i + 1),
                    comment_count=10 * (i + 1),
                    published_at=datetime(2024, 1, i + 1),
                    duration_seconds=180 + i * 10,
                    is_short=False
                )
                for i in range(5)
            ]

            # 4. 検索履歴に記録
            history_service = HistoryService(db_path)
            history = history_service.add_history(criteria, len(mock_videos))

            assert history is not None
            assert history.result_count == 5

            # 5. Excelにエクスポート
            exporter = ExcelExporter()
            exporter.export(mock_videos, excel_path)

            # 6. 検証
            assert os.path.exists(excel_path)
            assert os.path.getsize(excel_path) > 0

            # プリセットが保存されているか確認
            loaded_preset = preset_service.load_preset("Pythonチュートリアル")
            assert loaded_preset is not None
            assert loaded_preset.criteria.keyword == "Python tutorial"

            # 履歴が記録されているか確認
            recent_history = history_service.get_recent_history(limit=1)
            assert len(recent_history) == 1
            assert recent_history[0].criteria.keyword == "Python tutorial"
            assert recent_history[0].result_count == 5

        finally:
            # クリーンアップ
            if os.path.exists(db_path):
                os.unlink(db_path)
            if os.path.exists(excel_path):
                os.unlink(excel_path)
