import os

# ログの設定
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
LOG_FILE = os.environ.get("LOG_FILE", "application.log")
LOG_FORMAT = os.environ.get("LOG_FORMAT", None)  # ログフォーマット設定 (Noneの場合はlogger.pyでデフォルト値を使用)
LOG_ROTATION = os.environ.get("LOG_ROTATION", "1 week")  # ローテーション設定 (e.g., "100 MB", "500 KB", "1 week")
LOG_RETENTION = os.environ.get("LOG_RETENTION", "7 days") # 保存期間設定
LOG_ENCODING = os.environ.get("LOG_ENCODING", "utf-8")  # エンコーディング設定

# MongoDBの設定
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/") # デフォルトはローカルホスト
MONGODB_DB = os.environ.get("MONGODB_DB", "news_py") # データベース名

# CSSセレクタの設定
yahoo_SELECTORS = {
    "topics_page_link": '#uamods-topics p.sc-18b2wkl-1.gClYrK a',
    "article_links": '#uamods-topics ul li[data-ual-view-type="list"] a',
    "pickup_link": '#uamods-pickup > div.sc-gdv5m1-0.cuVskI > div.sc-gdv5m1-8.eMtbmz > a',
    "article_data_h1": '#uamods > header > h1, #uamods div.article_body.highLightSearchTarget p',
    "article_data_p": '#uamods div.article_body.highLightSearchTarget p, #uamods-article > div:nth-child(1) > section > div p',
    "article_data_time": '#uamods > header > div > div > p > time, #uamods-article > div:nth-child(1) > header > div > div.sc-1fea4ol-4.cbpbKO > div.sc-1fea4ol-7.bOXKxM > time',
    "comment": '#uamods > header > div > div > div.sc-1n9vtw0-0.hLzvcB > button:nth-child(1) > span',
    "author": '#uamods > footer > a, #contentsWrap > div > div > div > div.sc-150e8y2-2.fEbFen > div > div > a',
    "updated_at": '#uamods > footer > div > time',
    "article_data_p_link": '#uamods > div.sc-brfqoi-0.iHxBOa > div > ul > li:last-child a'
}

SITEURL = {
    "yahoo_top": 'https://news.yahoo.co.jp/',
    "yahoo_link": 'https://news.yahoo.co.jp/topics/top-picks'
}

# Slackの設定
SLACK_WEBHOOK_URL = os.environ.get("SLAKC_WEBHOOK_URL", "https://hooks.slack.com/services/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")

SCRAPE_INTERVAL = 1