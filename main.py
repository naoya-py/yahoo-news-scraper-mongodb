# main.py
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler  # 追加
from loggings.logger import get_logger
from tests.yahoo.test_yahoo_news import scrape_yahoo_news
import config  # config.py をインポート

logger = get_logger(__name__)

scheduler = BackgroundScheduler()
scrape_job = None  # ジョブオブジェクトを保持する変数を追加
run_status = "待機中"  # 実行状態を保持する変数


def scrape_task():
    """スクレイピングタスク (定期実行される関数)"""
    global run_status
    run_status = "実行中"
    logger.info("スクレイピングタスク開始")
    try:
        scrape_yahoo_news(headless=True, max_pages=config.MAX_PAGES)  # 設定を渡す
        run_status = "完了"
        logger.info("スクレイピングタスク完了")
    except Exception as e:
        run_status = f"エラー: {e}"
        logger.exception(f"スクレイピングタスク中にエラー発生: {e}")


def start_scheduler():
    """スケジューラを開始する"""
    global scrape_job
    if not scheduler.running:  # 既にスケジューラが動いている場合は再起動しない
        scrape_job = scheduler.add_job(
            scrape_task,
            'interval',
            hours=config.SCRAPE_INTERVAL,
            id='scrape_yahoo_news_job'  # ジョブIDを設定
        )
        scheduler.start()
        logger.info(f"スケジューラを開始しました。実行間隔: {config.SCRAPE_INTERVAL}時間")
    else:
        logger.info("スケジューラは既に実行中です。")


def stop_scheduler():
    """スケジューラを停止する"""
    global run_status
    if scheduler.running:
        scheduler.shutdown()
        run_status = "停止"  # 状態を更新
        logger.info("スケジューラを停止しました。")
    else:
        logger.info("スケジューラは既に停止しています。")


def get_next_run_time():
    """次回の実行時刻を取得する"""
    if scrape_job:
        return scrape_job.next_run_time
    return None


if __name__ == "__main__":
    try:
        logger.info("アプリケーションを開始します。")
        start_scheduler()  # スケジューラを開始

        while True:
            now = datetime.datetime.now()
            next_run_time = get_next_run_time()

            logger.info(f"現在時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            if next_run_time:
                logger.info(f"次回実行時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"ステータス: {run_status}")

            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("アプリケーションを停止します。")
        stop_scheduler()  # スケジューラを停止
    except Exception as e:
        logger.exception(f"予期せぬエラーが発生しました: {e}")