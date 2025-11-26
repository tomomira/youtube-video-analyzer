#!/usr/bin/env python3
"""
ロギング設定モジュール

アプリケーション全体で使用するロガーの設定を提供します。
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# ログレベルの設定（環境変数から取得、デフォルトはINFO）
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# ログフォーマット
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ログディレクトリのパス
LOG_DIR = Path(__file__).parent.parent.parent / 'logs'

# ロガーの辞書（シングルトンパターン）
_loggers = {}

def _ensure_log_directory():
    """ログディレクトリが存在することを確認"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    ロガーインスタンスを取得

    Args:
        name: ロガー名（通常は __name__ を渡す）
              Noneの場合は'youtube_analyzer'を使用

    Returns:
        logging.Logger: 設定済みのロガーインスタンス

    Example:
        >>> from src.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("処理を開始しました")
    """
    if name is None:
        name = 'youtube_analyzer'

    # すでに設定済みのロガーがあればそれを返す
    if name in _loggers:
        return _loggers[name]

    # 新しいロガーを作成
    logger = logging.getLogger(name)

    # ログレベルを設定
    try:
        level = getattr(logging, LOG_LEVEL)
    except AttributeError:
        level = logging.INFO
        print(f"警告: 無効なログレベル '{LOG_LEVEL}'。INFOを使用します。", file=sys.stderr)

    logger.setLevel(level)

    # すでにハンドラが設定されている場合はスキップ
    if logger.handlers:
        _loggers[name] = logger
        return logger

    # フォーマッターを作成
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # コンソールハンドラを追加
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラを追加
    try:
        _ensure_log_directory()
        log_file = LOG_DIR / 'youtube_analyzer.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"警告: ログファイルの作成に失敗しました: {e}", file=sys.stderr)

    # 親ロガーへの伝播を防ぐ（重複ログ出力を防止）
    logger.propagate = False

    # ロガーをキャッシュ
    _loggers[name] = logger

    return logger

def set_log_level(level: str):
    """
    実行時にログレベルを変更

    Args:
        level: ログレベル ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    try:
        log_level = getattr(logging, level.upper())
        for logger in _loggers.values():
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)
    except AttributeError:
        raise ValueError(f"無効なログレベル: {level}")

# デフォルトロガーを初期化
_default_logger = get_logger()

def debug(msg: str, *args, **kwargs):
    """デバッグレベルのログを出力"""
    _default_logger.debug(msg, *args, **kwargs)

def info(msg: str, *args, **kwargs):
    """情報レベルのログを出力"""
    _default_logger.info(msg, *args, **kwargs)

def warning(msg: str, *args, **kwargs):
    """警告レベルのログを出力"""
    _default_logger.warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs):
    """エラーレベルのログを出力"""
    _default_logger.error(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs):
    """致命的エラーレベルのログを出力"""
    _default_logger.critical(msg, *args, **kwargs)

# モジュールのテスト用
if __name__ == "__main__":
    # テスト用のログ出力
    test_logger = get_logger("test")

    test_logger.debug("これはDEBUGレベルのログです")
    test_logger.info("これはINFOレベルのログです")
    test_logger.warning("これはWARNINGレベルのログです")
    test_logger.error("これはERRORレベルのログです")
    test_logger.critical("これはCRITICALレベルのログです")

    print(f"\nログファイルの場所: {LOG_DIR / 'youtube_analyzer.log'}")
