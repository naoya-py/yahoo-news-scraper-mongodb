from apscheduler.schedulers.background import BackgroundScheduler
from tenacity import retry, stop_after_attempt, wait_fixed

import config  # config.pyのインポート
from loggings.logger import get_logger
from tests.yahoo.test_yahoo_news import scrape_yahoo_news

logger = get_logger(__name__)

scheduler = BackgroundScheduler()
scrape_job = None  # ジョブオブジェクトを保持
run_status = "待機中"

@retry(stop=stop_after_attempt(3), wait=wait_fixed(10)) # tenacityを使った再試行設定
def scrape_task():
    global run_status
    logger.info(f"ジョブID: {scrape_job.id} 実行開始") # ジョブIDをログに出力
    run_status = "実行中"
    try:
        scrape_yahoo_news()
        run_status = "完了"
    except Exception as e:
        run_status = f"エラー: {e}"
        logger.exception(f"ジョブID: {scrape_job.id} 実行中にエラーが発生しました: {e}")
    finally:
        logger.info(f"ジョブID: {scrape_job.id} 実行終了")

def start_scheduler():
    global scrape_job
    scrape_job = scheduler.add_job(
        scrape_task, 'interval', hours=config.SCRAPE_INTERVAL, id='scrape_job'
    )
    scheduler.start()


def stop_scheduler():
    scheduler.shutdown()

def get_next_run_time():
    """次回の実行時刻を取得する"""
    if scrape_job:
        return scrape_job.next_run_time
    return None