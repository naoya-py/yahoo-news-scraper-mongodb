import time
import datetime
from scheduler import tasks
from loggings.logger import get_logger


logger = get_logger(__name__)

if __name__ == "__main__":
    try:
        logger.info("スクレイピングを開始します。")
        tasks.start_scheduler() # スケジューラを開始

        while True:
            now = datetime.datetime.now()
            next_run_time = tasks.get_next_run_time()
            run_status = tasks.run_status

            logger.info(f"最終実行時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            if next_run_time:
                logger.info(f"次回実行時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"ステータス: {run_status}")

            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("スクレイピングを停止します。")
        tasks.stop_scheduler() # スケジューラを停止
    except Exception as e:
        logger.exception(f"予期せぬエラーが発生しました: {e}")