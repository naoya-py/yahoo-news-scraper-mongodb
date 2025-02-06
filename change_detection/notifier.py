from slack_sdk.webhook import WebhookClient

def send_notification(message):
    """
    変更通知をSlackに送信する

    Args:
        message: 通知メッセージ
    """
    try:
        url = "https://hooks.slack.com/services/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"
        webhook = WebhookClient(url)

        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
        print("Slackへの通知に成功しました。")

    except Exception as e:
        print(f"Slackへの通知に失敗しました: {e}")