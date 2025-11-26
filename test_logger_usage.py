#!/usr/bin/env python3
"""
ロガー使用例のデモスクリプト

各モジュールでのロガーの使用方法を示します。
"""

from src.utils.logger import get_logger

# モジュール固有のロガーを取得
logger = get_logger(__name__)

def main():
    """ロガーの使用例"""
    logger.info("=" * 60)
    logger.info("ロガー使用例デモ")
    logger.info("=" * 60)

    # 各種ログレベルの例
    logger.debug("デバッグ情報: 変数の値を確認する際に使用")
    logger.info("情報: 通常の処理の進捗状況")
    logger.warning("警告: 問題が発生する可能性がある状況")
    logger.error("エラー: 処理が失敗したが、プログラムは継続可能")
    logger.critical("致命的: プログラムの継続が困難な重大なエラー")

    # 実際の使用例
    logger.info("")
    logger.info("実際の使用例:")
    logger.info("-" * 60)

    # 1. 処理開始のログ
    video_keyword = "Python tutorial"
    min_views = 1000000
    logger.info(f"動画検索を開始: キーワード='{video_keyword}', 最小再生回数={min_views:,}")

    # 2. 進捗のログ
    logger.info("YouTube APIに接続中...")
    logger.info("検索クエリを実行中...")

    # 3. 結果のログ
    found_videos = 25
    logger.info(f"検索完了: {found_videos}件の動画を取得しました")

    # 4. 警告のログ（API制限に近づいている場合など）
    remaining_quota = 500
    if remaining_quota < 1000:
        logger.warning(f"APIクォータ残量が少なくなっています: 残り{remaining_quota}ユニット")

    # 5. エラーのログ（例外をキャッチした場合）
    try:
        # エラーをシミュレート
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"計算エラーが発生しました: {e}", exc_info=True)

    logger.info("")
    logger.info("=" * 60)
    logger.info("デモ完了")
    logger.info("=" * 60)
    logger.info(f"ログファイルを確認してください: logs/youtube_analyzer.log")

if __name__ == "__main__":
    main()
