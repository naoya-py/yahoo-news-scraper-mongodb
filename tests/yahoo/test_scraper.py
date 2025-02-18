import pytest
from playwright.sync_api import sync_playwright
from scrapers.yahoo.yahoo_news import (clean_text, scrape_article_data,
                                        get_article_links, scrape_paginated_content)
from config import yahoo_SELECTORS

# テスト用の簡単なHTMLを用意
TEST_HTML = """
<h1>テスト記事タイトル</h1>
<p>テスト記事本文1</p>
<p>テスト記事本文2</p>
<time>2024/01/01(月) 00:00</time>
<div class="author">テスト著者</div>
<a href="https://example.com/article1">記事1</a>
<a href="/article2">記事2</a> <a href="http://example.com/article3">記事3</a>

"""

TEST_HTML_PAGINATED = """
<h1>テスト記事タイトル</h1>
<p>ページ1のコンテンツ</p>
<a href="?page=2">次のページ</a>
"""

TEST_HTML_PAGINATED_2 = """
<h1>テスト記事タイトル</h1>
<p>ページ2のコンテンツ</p>
"""




@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_clean_text():
    text = "<p>テストテキスト<br>改行</p>"
    cleaned_text = clean_text(text)
    assert cleaned_text == "テストテキスト 改行"


def test_scrape_article_data(page):
    page.set_content(TEST_HTML)
    article_data = scrape_article_data(page, "test_url")

    assert article_data.title == "テスト記事タイトル"
    assert article_data.content == "テスト記事本文1 テスト記事本文2"
    assert article_data.author == "テスト著者"
    assert article_data.published_at == "2024-01-01 00:00:00"
    assert article_data.url == "test_url"



def test_get_article_links(page):
    page.set_content(TEST_HTML)
    links = get_article_links(page)
    assert links == ["https://example.com/article1", "http://example.com/article3"]



def test_scrape_paginated_content(page, monkeypatch):

    def mock_goto(self, url, **kwargs):

        if url.endswith("?page=1"):
            self.set_content(TEST_HTML_PAGINATED)
        elif url.endswith("?page=2"):
            self.set_content(TEST_HTML_PAGINATED_2)
        else:
            raise Exception("Unexpected URL")

        # mock のレスポンスを返す
        class MockResponse:
            status = 200

        return MockResponse()

    monkeypatch.setattr("playwright.sync_api._generated.Page.goto", mock_goto)

    additional_texts = scrape_paginated_content(page)
    assert additional_texts == ["ページ1のコンテンツ", "ページ2のコンテンツ"]