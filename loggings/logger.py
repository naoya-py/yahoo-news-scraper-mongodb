import sys
from loguru import logger
from pathlib import Path
import config  # config.py をインポート


def get_logger(name=__name__): # nameのデフォルト値を設定
    """
    config.py で設定された値を使ってロガーを取得します。
    """

    logger.remove()  # 既存のハンドラをクリア


    # 標準出力へのログ設定 (stderr を使用)
    logger.add(
        sys.stderr,
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
        backtrace=True,
        diagnose=True,
        enqueue=True
    )

    # ファイル出力へのログ設定 (config.LOG_FILE が指定されている場合)
    if config.LOG_FILE:
        log_file: Path = Path(config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_file,
            level=config.LOG_LEVEL,
            rotation=config.LOG_ROTATION,
            retention=config.LOG_RETENTION,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}",
            backtrace=True,
            diagnose=True,
            encoding=config.LOG_ENCODING,
            enqueue=True,
        )

    return logger.bind(name=name)

