from playwright.sync_api import sync_playwright
from loggings.logger import get_logger
from utils.network import get_random_user_agent
from playwright_stealth import stealth_sync

logger = get_logger()

def scrape_article_data(page):
    try:
        h1_text = page.query_selector('#uamods > header > h1').text_content()
        p_texts = [p.text_content() for p in page.query_selector_all('.article_body p')]
        logger.debug(f"記事データ取得成功: h1={h1_text}")
        return {
            'h1': h1_text,
            'p': p_texts,
        }
    except Exception as e:
        logger.error(f"記事データの取得に失敗しました: {e}")
        return None

def scrape_article_data2(page):
    try:
        h1_text = page.query_selector('#uamods-article > div:nth-child(1) > header > h1').text_content()
        p_texts = [p.text_content() for p in page.query_selector_all('#uamods-article > div:nth-child(1) > section > div > p')]
        logger.debug(f"記事データ取得成功: h1={h1_text}")
        return {
            'h1': h1_text,
            'p': p_texts,
        }
    except Exception as e:
        logger.error(f"記事データの取得に失敗しました: {e}")
        return None

def get_article_links(page):
    links = []
    for link in page.query_selector_all('#uamods-topics ul li[data-ual-view-type="list"] a'):
        if link:
            href = link.get_attribute('href')
            links.append(href)
    logger.debug(f"記事リンク取得: {len(links)}件")
    return links

def scrape_article_page(page):
    try:
        page.wait_for_load_state()
        pickup_link = page.locator('#uamods-pickup > div.sc-gdv5m1-0.cuVskI > div.sc-gdv5m1-8.eMtbmz > a')
        if pickup_link.count() > 0:
            # ピックアップ記事へのリンクがある場合の処理
            pickup_link.click()
            page.wait_for_load_state()
            article_data = scrape_article_data(page)
            if article_data:
                logger.info(f"記事データ取得成功: {article_data['h1'][:20]}...")
                # TODO: 必要に応じてデータを保存する処理を追加
            page.go_back()
            page.wait_for_load_state()
            page.go_back()
            page.wait_for_load_state()

        else:
            # ピックアップ記事へのリンクがない場合の処理
            logger.info("記事全文を読むのリンクがありません。h1とpを抽出します。")
            article_data = scrape_article_data2(page)
            if article_data:
                logger.info(f"記事データ取得成功: {article_data['h1'][:20]}...")
                # TODO: 必要に応じてデータを保存する処理を追加
            page.go_back()
            page.wait_for_load_state()

    except Exception as e:
        logger.error(f"記事ページの処理中にエラー発生: {page.url} - {e}")


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


def scrape_yahoo_news():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=get_random_user_agent())
            stealth_sync(page)
            try:
                page.goto('https://news.yahoo.co.jp/')
                logger.info("Yahoo!トップページへアクセス")

                page.locator('#uamods-topics p.sc-18b2wkl-1.gClYrK a').click()
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