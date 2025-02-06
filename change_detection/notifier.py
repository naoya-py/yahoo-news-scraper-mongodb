from slack_sdk.webhook import WebhookClient
from loggings.logger import get_logger
from config import SLACK_WEBHOOK_URL

logger = get_logger(__name__)

def send_notification(message):
    """
    変更通知をSlackに送信する

    Args:
        message: 通知メッセージ
    """
    try:
        url = SLACK_WEBHOOK_URL
        webhook = WebhookClient(url)
        logger.debug(f"Slackへの通知を試行します。message={message}") # デバッグログを追加

        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
        logger.info("Slackへの通知に成功しました。") # 成功ログを追加

    except AssertionError as e:
        logger.error(f"Slackへの通知に失敗しました: {e}") # 失敗ログを追加 (AssertionError)
        logger.debug(f"response.status_code={response.status_code}, response.body={response.body}") # デバッグログを追加
    except Exception as e:
        logger.exception(f"Slackへの通知に失敗しました: {e}")