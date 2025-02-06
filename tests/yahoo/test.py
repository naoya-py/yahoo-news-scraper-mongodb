from playwright.sync_api import sync_playwright
from loggings.logger import get_logger
from utils.network import get_random_user_agent
from playwright_stealth import stealth_sync
from utils import database
from retry import retry
from config import yahoo_SELECTORS
from utils.parser import remove_html_tags, decode_html_entities, normalize_text, remove_extra_whitespaces, parse_datetime_from_html, format_datetime
from change_detection import detector

logger = get_logger(__name__)

def clean_text(text):
    """テキストをクレンジングするヘルパー関数"""
    text = remove_html_tags(text)
    text = decode_html_entities(text)
    text = normalize_text(text)
    text = remove_extra_whitespaces(text)
    return text

@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_article_data(page):
    try:
        h1_element = page.query_selector(yahoo_SELECTORS["article_data_h1"])
        h1_text = h1_element.inner_html() if h1_element else "" # innerHTMLに変更
        h1_text = clean_text(h1_text) # テキストクレンジング

        time_element = page.query_selector(yahoo_SELECTORS["article_data_time"])
        time_text = time_element.inner_html() if time_element else ""
        time_text = clean_text(time_text)
        datetime_object = parse_datetime_from_html(time_text)
        formattime = format_datetime(datetime_object)

        p_texts = []
        for p in page.query_selector_all(yahoo_SELECTORS["article_data_p"]):
            p_text = p.inner_html()  # innerHTMLに変更
            p_text = clean_text(p_text) # テキストクレンジング
            p_texts.append(p_text)

        logger.debug(f"記事データ取得成功: h1={h1_text}")
        return {
            'h1': h1_text,
            'p': p_texts,
            'time': formattime,
        }
    except Exception as e:
        logger.error(f"記事データの取得に失敗しました: {e}")
        return None

@retry(tries=3, delay=5, backoff=2, logger=logger)
def get_article_links(page):
    links = []
    for link in page.query_selector_all(yahoo_SELECTORS["article_links"]):
        if link:
            href = link.get_attribute('href')
            links.append(href)
    logger.debug(f"記事リンク取得: {len(links)}件")
    return links

@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_article_page(page):
    try:
        page.wait_for_load_state()
        pickup_link = page.locator(yahoo_SELECTORS["pickup_link"])
        if pickup_link.count() > 0:
            # ピックアップ記事へのリンクがある場合の処理
            pickup_link.click()
            page.wait_for_load_state()
            article_data = scrape_article_data(page)
            if article_data:
                logger.info(f"記事データ取得成功: {article_data['h1'][:20]}...")
                database.save_data(article_data, 'news_paper')

                selectors = {  # 変更を監視するセレクタを指定
                    "article_data_h1": yahoo_SELECTORS["article_data_h1"],
                    "article_data_time": yahoo_SELECTORS["article_data_time"],
                    "article_data_p": yahoo_SELECTORS["article_data_p"],
                }
                if detector.detect_change(page, page.url, selectors):
                    logger.info(f"ページ {page.url} の変更を検知しました。")

            page.go_back()
            page.wait_for_load_state()
            page.go_back()
            page.wait_for_load_state()

        else:
            # ピックアップ記事へのリンクがない場合の処理
            logger.info("記事全文を読むのリンクがありません。h1とpを抽出します。")
            article_data = scrape_article_data(page)
            if article_data:
                logger.info(f"記事データ取得成功: {article_data['h1'][:20]}...")
                database.save_data(article_data, 'news_paper')
            page.go_back()
            page.wait_for_load_state()

    except Exception as e:
        logger.error(f"記事ページの処理中にエラー発生: {page.url} - {e}")

@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_article_list_page(page):
    current_page = 1
    topics_url = "https://news.yahoo.co.jp/topics/top-picks"  # URLを定数化

    try:
        while True:
            logger.info(f"ページ {current_page} をスクレイピング開始")
            page.goto(f"{topics_url}?page={current_page}", wait_until="load")
            page.wait_for_load_state()

            links = get_article_links(page)

            if not links:
                logger.info("記事一覧ページに記事へのリンクがありません。処理を終了します。")
                break  # 記事リンクがない場合はループを抜ける

            for link in links:
                try:
                    page.goto(link, wait_until="load")
                    page.wait_for_load_state()
                    logger.debug(f"記事ページへ遷移: {link}")
                    scrape_article_page(page)

                except Exception as e:
                    logger.error(f"記事ページの処理中にエラー発生: {link} - {e}")

            current_page += 1

    except Exception as e:
        logger.critical(f"致命的なエラー発生: {e}")
    finally:
        logger.info("スクレイピング完了")

@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_yahoo_news():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=get_random_user_agent())
            stealth_sync(page)
            try:
                page.goto('https://news.yahoo.co.jp/')
                logger.info("Yahoo!トップページへアクセス")
                page.wait_for_load_state()

                page.locator(yahoo_SELECTORS["topics_page_link"]).click()
                page.wait_for_load_state()

                logger.info("最初のトピックページへ遷移")

                scrape_article_list_page(page)

            finally:
                page.close()
                browser.close()

    except Exception as e:
        logger.critical(f"致命的なエラー: {e}")

if __name__ == "__main__":
    scrape_yahoo_news()