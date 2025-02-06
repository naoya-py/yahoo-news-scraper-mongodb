import hashlib
import json
from change_detection.notifier import send_notification
from utils.parser import remove_html_tags, decode_html_entities, normalize_text, remove_extra_whitespaces
from loggings.logger import get_logger

logger = get_logger(__name__)

def clean_text(text):
    """テキストをクレンジングするヘルパー関数"""
    text = remove_html_tags(text)
    text = decode_html_entities(text)
    text = normalize_text(text)
    text = remove_extra_whitespaces(text)
    return text

def detect_change(page, url, selectors):
    """
    指定されたセレクタの要素のHTML構造の変化を検知する

    Args:
        page: PlaywrightのPageオブジェクト
        url: ページのURL
        selectors: 変更を監視する要素のセレクタ（辞書形式）

    Returns:
        bool: 変更があった場合はTrue、そうでない場合はFalse
    """
    try:
        logger.debug(f"変更検知開始: {url}")  # 変更検知開始のログ

        # 1. ページのHTMLを取得
        page.goto(url, wait_until='networkidle')
        extracted_texts = {}
        for selector_name, selector in selectors.items():
            elements = page.query_selector_all(selector)
            texts = []
            if elements:
                for element in elements:
                    text_content = clean_text(element.inner_text())
                    texts.append(text_content)
                logger.debug(f"セレクタ {selector_name} のテキスト抽出完了: {len(texts)}件")  # 抽出完了のログ
            else:
                logger.warning(f"セレクタ {selector_name} に一致する要素が見つかりませんでした")  # 要素が見つからない場合のログ
            extracted_texts[selector_name] = texts

        # 2. ハッシュ値を計算
        current_hash = hashlib.sha256(json.dumps(extracted_texts, sort_keys=True).encode()).hexdigest()
        logger.debug(f"現在ハッシュ値: {current_hash}")  # ハッシュ値のログ

        # 3. 過去のハッシュ値と比較
        page_hashes = {}
        try:
            with open('page_hashes.json', 'r') as f:
                page_hashes = json.load(f)
        except FileNotFoundError:
            logger.debug("page_hashes.json が見つかりません。新規作成します。")  # ファイルがない場合のログ

        previous_data = page_hashes.get(url)
        previous_hash = previous_data.get('hash') if previous_data else None
        logger.debug(f"過去ハッシュ値: {previous_hash}")

        if previous_hash is None or current_hash != previous_hash:
            # 4. ハッシュ値とテキストを保存
            page_hashes[url] = {'hash': current_hash, 'texts': json.dumps(extracted_texts)}
            with open('page_hashes.json', 'w') as f:
                json.dump(page_hashes, f, indent=4, ensure_ascii=False)

            # 5. 変更があったセレクタ名を取得
            previous_texts = json.loads(previous_data.get('texts', "{}") if previous_data else "{}")
            changed_selectors = [key for key in extracted_texts if extracted_texts[key] != previous_texts.get(key)]

            # 6. 通知
            message = f"ページ {url} の以下の要素が変更されました:\n" + "\n".join(changed_selectors)  # 変更されたセレクタ名だけを通知
            send_notification(message)
            logger.info(f"ページ {url} の変更を検知しました。変更されたセレクタ: {changed_selectors}")  # 変更検知のログ
            return True

        logger.debug(f"ページ {url} に変更はありません。")  # 変更がない場合のログ
        return False


    except Exception as e:
        logger.error(f"変更検知中にエラーが発生しました: {e}")  # エラーログ
        return False