from playwright.sync_api import sync_playwright
from utils import parser  # parser.pyをインポート

def test_parser_with_playwright(url, selector):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)

        element = page.query_selector(selector)
        if element:
            html_snippet = element.inner_html() if element else ""

            # parser.pyの関数で変換
            cleaned_text = parser.remove_html_tags(html_snippet)
            decoded_text = parser.decode_html_entities(cleaned_text)
            normalized_text = parser.normalize_text(cleaned_text)
            extra_ws_removed = parser.remove_extra_whitespaces(normalized_text)
            datetime_obj = parser.parse_datetime_from_html(extra_ws_removed)
            formatted_datetime = parser.format_datetime(datetime_obj)


            print(f"元のHTML: {html_snippet}")
            print(f"HTMLタグ除去後: {cleaned_text}")
            print(f"HTMLエンティティデコード後: {decoded_text}")
            print(f"正規化後: {normalized_text}")
            print(f"空白削除後: {extra_ws_removed}")
            print(f"日付時刻オブジェクト: {datetime_obj}")
            print(f"フォーマット済み日付時刻: {formatted_datetime}")

        else:
            print(f"セレクター '{selector}' に一致する要素は見つかりませんでした。")

        browser.close()

if __name__ == "__main__":
    target_url = input("URLを入力してください: ")
    target_selector = input("セレクターを入力してください: ")
    test_parser_with_playwright(target_url, target_selector)