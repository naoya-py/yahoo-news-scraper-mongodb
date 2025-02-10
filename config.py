import os

# ログの設定
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.environ.get("LOG_FILE", "application.log")
LOG_FORMAT = os.environ.get("LOG_FORMAT", None)  # None の場合は logger.py でデフォルト値を使用
LOG_ROTATION = os.environ.get("LOG_ROTATION", "1 week")
LOG_RETENTION = os.environ.get("LOG_RETENTION", "7 days")
LOG_ENCODING = os.environ.get("LOG_ENCODING", "utf-8")

# MongoDB の設定
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.environ.get("MONGODB_DB", "news_py")

# CSS セレクタの設定
# セレクタをカテゴリ分けして整理。可読性と保守性を向上。
yahoo_SELECTORS = {
    "navigation": {
        "topics_page_link": "#uamods-topics p.sc-18b2wkl-1.gClYrK a",
        "article_links": "#uamods-topics ul li[data-ual-view-type=\"list\"] a",
        "pickup_link": "#uamods-pickup > div.sc-gdv5m1-0.cuVskI > div.sc-gdv5m1-8.eMtbmz > a",
        "article_data_p_link": "#uamods > div.sc-brfqoi-0.iHxBOa > div > ul > li:last-child a", # 分割記事リンク
        "page_link": "#contentsWrap > div > div.sc-brfqoi-0.ehBQrA > div > ul > li:last-child > a", # 次ページリンク
    },
    "article_content": {
        "article_data_h1": "#uamods > header > h1, #uamods div.article_body.highLightSearchTarget p, #uamods-article > div:nth-child(1) > header > h1",
        "article_data_p": "#uamods div.article_body.highLightSearchTarget p, #uamods-article > div:nth-child(1) > section > div p, #uamods > div.article_body.highLightSearchTarget > div:nth-child(1) > p",
        "article_data_time": "#uamods > header > div > div > p > time, #uamods-article > div:nth-child(1) > header > div > div.sc-1fea4ol-4.cbpbKO > div.sc-1fea4ol-7.bOXKxM > time",
        "comment": "#uamods > header > div > div > div.sc-1n9vtw0-0.hLzvcB > button:nth-child(1) > span",
        "author": "#uamods > footer > a, #contentsWrap > div > div > div > div.sc-150e8y2-2.fEbFen > div > div > a",
        "updated_at": "#uamods > footer > div > time",

    }
}


# サイト URL の設定
SITEURL = {
    "yahoo_top": "https://news.yahoo.co.jp/",
    "yahoo_link": "https://news.yahoo.co.jp/topics/top-picks",
}

# Slack の設定
# "SLAKC_WEBHOOK_URL" はtypoの可能性があるので、"SLACK_WEBHOOK_URL" に修正
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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") # ダミーURLは良くないので、変数設定されていなければNoneにする

SCRAPE_INTERVAL = 1 # 用途が不明瞭なので、一旦残すが、使用箇所で意味のある名前に変更する

# スクレイピングの間隔（時間単位）
SCRAPE_INTERVAL = 3

# スクレイピングする最大ページ数
MAX_PAGES = 5