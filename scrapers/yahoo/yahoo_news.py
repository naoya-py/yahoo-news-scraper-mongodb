from playwright.sync_api import sync_playwright
from loggings.logger import get_logger
from utils.network import get_random_user_agent
from playwright_stealth import stealth_sync
from utils import database
from retry import retry
from config import yahoo_SELECTORS, SITEURL
from utils.parser import (remove_html_tags, decode_html_entities,
                            normalize_text, remove_extra_whitespaces,
                            parse_datetime_from_html, format_datetime)
from change_detection import detector
from models.article import Article
import time
import random

logger = get_logger(__name__)

def clean_text(text):
    """テキストをクレンジングするヘルパー関数"""
    if not text:
        return ""
    text = remove_html_tags(text)
    text = decode_html_entities(text)
    text = normalize_text(text)
    text = remove_extra_whitespaces(text)
    return text

def scrape_and_save_article(page, url, additional_texts=None):
    """記事データをスクレイピングし、データベースに保存する関数"""
    article_data = scrape_article_data(page, url, additional_texts)
    if article_data:
        logger.info(f"データ取得成功: {article_data.title}")
        database.save_data(article_data, 'news_paper')

        if detector.detect_change(page, url, yahoo_SELECTORS):
            logger.info(f"ページ {url} の変更を検知しました。")


@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_article_data(page, url, additional_texts=None):
    """
    記事の詳細データをスクレイピングする関数。リトライ処理付き。
    additional_texts: 分割された記事のテキストリスト (オプション)
    """
    try:
        if url is None:
            logger.warning("URL が None のため、記事データの取得をスキップします。")
            return None

        h1_element = page.locator(yahoo_SELECTORS["article_content"]["article_data_h1"]).first
        h1_text = clean_text(h1_element.inner_html()) if h1_element and h1_element.is_visible() else ""

        coment_element = page.locator(yahoo_SELECTORS["article_content"]["comment"]).first
        coment_text = clean_text(coment_element.inner_html()) if coment_element and coment_element.is_visible() else ""

        author_element = page.locator(yahoo_SELECTORS["article_content"]["author"]).first
        author_text = clean_text(author_element.inner_html()) if author_element and author_element.is_visible() else ""

        # time 要素の取得とエラーハンドリング
        time_element = page.locator(yahoo_SELECTORS["article_content"]["article_data_time"]).first
        if time_element and time_element.is_visible():
            time_text = clean_text(time_element.inner_html())
            datetime_object = parse_datetime_from_html(time_text) if time_text else None
            formattime = format_datetime(datetime_object) if datetime_object else None
        else:
            logger.warning(f"time要素が見つかりません: {url}")  # ログ出力
            formattime = None

        # updated_at 要素の取得とエラーハンドリング
        updated_at_element = page.locator(yahoo_SELECTORS["article_content"]["article_data_time"]).first # time要素と同じセレクタになっているので注意
        if updated_at_element and updated_at_element.is_visible():
            updated_at_text = clean_text(updated_at_element.inner_html())
            updated_object = parse_datetime_from_html(updated_at_text) if updated_at_text else None
            updated_at_formattime = format_datetime(updated_object) if updated_object else None
        else:
            logger.warning(f"updated_at要素が見つかりません: {url}")  # ログ出力
            updated_at_formattime = None

        p_texts = []
        for p in page.locator(yahoo_SELECTORS["article_content"]["article_data_p"]).all():
            if p.is_visible():
                p_text = clean_text(p.inner_html())
                if p_text:
                    p_texts.append(p_text)

        if additional_texts:
            p_texts.extend(additional_texts)

        return Article(
            url=url,
            title=h1_text,
            content=" ".join(p_texts),
            coment=coment_text,
            author=author_text,
            published_at=formattime,
            updated_at=updated_at_formattime,
            source={"site_name": "yahoo", "url": SITEURL["yahoo_top"]}
        )
    except Exception as e:
        logger.error(f"データの取得に失敗: {url} - {e}")
        return None



@retry(tries=3, delay=5, backoff=2, logger=logger)
def get_article_links(page):
    """記事一覧ページから記事へのリンクを取得する関数"""
    links = []
    for link in page.locator(yahoo_SELECTORS["navigation"]["article_links"]).all():
        href = link.get_attribute('href')
        if href and href.startswith("http"):
            links.append(href)
    logger.debug(f"記事リンク取得: {len(links)}件")
    return links



@retry(tries=3, delay=5, backoff=2, logger=logger)
def scrape_article_page(page, url):
    """個別の記事ページをスクレイピングする関数"""
    try:
        page.goto(url, wait_until="load")
        page.wait_for_load_state(timeout=10000)

        pickup_link = page.locator(yahoo_SELECTORS["navigation"]["pickup_link"]).first
        if pickup_link and pickup_link.is_visible():
            pickup_link.click()
            page.wait_for_load_state(timeout=10000)


        # 分割記事の処理を関数化し、可読性向上
        additional_texts = scrape_paginated_content(page)
        scrape_and_save_article(page, url, additional_texts)

        page.go_back()
        page.wait_for_load_state(timeout=10000)
        if 'pickup' in url:  # ピックアップ記事から戻った場合はさらに戻る
            page.go_back()
            page.wait_for_load_state(timeout=10000)


    except Exception as e:
        logger.error(f"記事ページの処理中にエラー発生: {url} - {e}")


def scrape_paginated_content(page):
    """
    分割された記事のコンテンツをスクレイピングする関数
    """
    additional_texts = []
    current_page_num = 1
    base_url = page.url.split('?')[0]  # クエリパラメータを除去したベースURL

    while True:
        current_url = f"{base_url}?page={current_page_num}"
        logger.info(f"分割記事ページ {current_url} をスクレイピング")
        response = page.goto(current_url, wait_until="load")
        page.wait_for_load_state(timeout=10000)

        if response is None or response.status != 200:
            logger.info(f"分割記事ページが存在しません: {current_url}")
            break

        # 現在のページのコンテンツを取得
        for p in page.locator(yahoo_SELECTORS["article_content"]["article_data_p"]).all():
            if p.is_visible():
                p_text = clean_text(p.inner_html())
                if p_text:
                    additional_texts.append(p_text)

        # 次のページが存在するか確認 (セレクタを修正)
        next_page_link = page.locator(yahoo_SELECTORS["navigation"]["article_data_p_link"]).nth(current_page_num -1)
        if not next_page_link.is_visible():
            break


        current_page_num += 1
        time.sleep(random.uniform(1, 3))

    return additional_texts



def scrape_article_list_page(page, max_pages=100):
    """
    記事一覧ページをスクレイピングし、各記事ページへ遷移する関数。
    最大ページ数を設定可能。
    """
    topics_url = SITEURL["yahoo_link"]
    current_page = 1

    try:
        while current_page <= max_pages:
            url = f"{topics_url}?page={current_page}"
            logger.info(f"ページ {current_page} ({url}) をスクレイピング開始")

            response = page.goto(url, wait_until="load")
            page.wait_for_load_state(timeout=10000)

            if response and response.status != 200:
                logger.info(f"ページが存在しません: {url}")
                break
            elif response is None:
                logger.error(f"ページへのリクエストが失敗しました: {url}")
                break

            links = get_article_links(page)
            if not links:
                logger.info("記事一覧ページに記事へのリンクがありません。")
                break


            for link in links:
                try:
                    # scrape_article_page に URL を渡すように変更
                    scrape_article_page(page, link)
                    time.sleep(random.uniform(1, 3))


                except Exception as e:
                    logger.error(f"記事ページの処理中にエラー発生: {link} - {e}")

            current_page += 1
            time.sleep(random.uniform(2, 5))

    except Exception as e:
        logger.critical(f"致命的なエラー発生: {e}")
    finally:
        logger.info("スクレイピング完了")


def scrape_yahoo_news(headless=False, max_pages=100):
    """Yahoo!ニュースのスクレイピングを行うメイン関数"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page(user_agent=get_random_user_agent())
            stealth_sync(page)
            try:
                page.goto(SITEURL["yahoo_top"], wait_until="load")
                logger.info("Yahoo!トップページへアクセス")
                page.wait_for_load_state(timeout=10000)

                topics_page_link = page.locator(yahoo_SELECTORS["navigation"]["topics_page_link"]).first
                if topics_page_link and topics_page_link.is_visible():
                    topics_page_link.click()
                    page.wait_for_load_state(timeout=10000)
                else:
                    logger.error("トピックスページへのリンクが見つかりません")
                    return

                logger.info("トピックスページへ遷移")

                scrape_article_list_page(page, max_pages)

            finally:
                page.close()
                browser.close()

    except Exception as e:
        logger.critical(f"致命的なエラー: {e}")


if __name__ == "__main__":
    scrape_yahoo_news(headless=True, max_pages=40)