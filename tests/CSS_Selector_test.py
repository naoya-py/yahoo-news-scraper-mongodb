from playwright.sync_api import sync_playwright
import time

def inspect_selectors(url, selectors):
    """
    指定されたURLのページで、複数のセレクターに一致する要素を検査します。

    Args:
        url: 検査対象のURL
        selectors: 検査対象のセレクターのリスト
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url)

        try:
            for selector in selectors:
                try:
                    # セレクターに一致する要素を強調表示
                    element_count = page.evaluate("""
                        (selector) => {
                            const elements = document.querySelectorAll(selector);
                            for (const element of elements) {
                                element.style.border = '3px solid red'; // 既存のスタイルを上書きしないように変更
                            }
                            return elements.length;
                        }
                    """, selector)


                    if element_count > 0:
                        print(f"\nセレクター '{selector}' に一致する要素が {element_count} 件見つかりました。")
                        elements = page.query_selector_all(selector)
                        for i, element in enumerate(elements):
                            print(f"\n要素 {i + 1}:")
                            print(f"  テキスト: {element.inner_text()}")
                            print(f"  HTML: {element.inner_html()}")
                            print(f"  outerHTML: {element.evaluate('element => element.outerHTML')}")

                    else:
                        print(f"\nセレクター '{selector}' に一致する要素は見つかりませんでした。")


                except Exception as e:
                    print(f"セレクター '{selector}' の処理中にエラー: {e}")


            time.sleep(5)  # 20秒間、ブラウザを開いたままにする

        except Exception as e:
            print(f"エラー: {e}")
        finally:
            page.close()
            browser.close()


if __name__ == "__main__":
    target_url = input("URLを入力してください: ")
    target_selectors = []
    while True:
        selector = input("セレクターを入力してください (終了するには空行): ")
        if not selector:
            break
        target_selectors.append(selector)

    if target_selectors:  # セレクターが入力されている場合のみ実行
        inspect_selectors(target_url, target_selectors)