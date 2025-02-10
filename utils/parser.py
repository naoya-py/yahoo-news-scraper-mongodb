import html
import unicodedata
from bs4 import BeautifulSoup
import datetime
from loggings.logger import get_logger
import re
from langdetect import detect, LangDetectException

logger = get_logger(__name__)


def remove_html_tags(text):
    """
    HTMLタグを除去する

    Args:
        text: HTMLタグを含むテキスト

    Returns:
        str: HTMLタグが除去されたテキスト
    """
    logger.debug(f"remove_html_tags 関数が呼ばれました。text={text[:50]}...") # 引数の内容を一部ログ出力
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = soup.get_text(separator=' ', strip=True)
    logger.debug(f"remove_html_tags 関数が終了しました。cleaned_text={cleaned_text[:50]}...") # 戻り値の内容を一部ログ出力
    return cleaned_text

def decode_html_entities(text):
    """
    HTMLエンティティをデコードする

    Args:
        text: HTMLエンティティを含むテキスト

    Returns:
        str: HTMLエンティティがデコードされたテキスト
    """
    logger.debug(f"decode_html_entities 関数が呼ばれました。text={text[:50]}...")
    decoded_text = html.unescape(text) if text else text # None対策
    logger.debug(f"decode_html_entities 関数が終了しました。decoded_text={decoded_text[:50]}...")
    return decoded_text

def normalize_text(text):
    """
    テキストを正規化する

    Args:
        text: 正規化対象のテキスト

    Returns:
        str: 正規化されたテキスト
    """
    logger.debug(f"normalize_text 関数が呼ばれました。text={text[:50]}...")
    normalized_text = unicodedata.normalize('NFKC', text) if text else text
    logger.debug(f"normalize_text 関数が終了しました。normalized_text={normalized_text[:50]}...")
    return normalized_text

def remove_extra_whitespaces(text):
    """
    不要な空白を削除する。
    全角空白と半角空白に対応。
    textが文字列でない場合は、そのまま返す。
    """
    logger.debug(f"remove_extra_whitespaces 関数が呼ばれました。text={text[:50]}...")
    if not isinstance(text, str):
        return text
    text = text.strip()
    text = re.sub(r'[ 　]+', ' ', text)
    logger.debug(f"remove_extra_whitespaces 関数が終了しました。text={text[:50]}...")
    return text

def parse_datetime_from_html(html_snippet):
    """
    HTMLスニペットからdatetimeオブジェクトを生成する。
    複数のdatetimeフォーマットに対応。
    """
    logger.debug(f"parse_datetime_from_html 関数が呼ばれました。html_snippet={html_snippet[:50]}...")
    formats = [r"(\d+)/(\d+)\(.+?\)\s*(\d+):(\d+)"]
    for fmt in formats:
        match = re.search(fmt, html_snippet)
        if match:
            extracted_values = match.groups()
            if fmt == formats[0]:  # 最初の形式の場合、年を補完
                current_year = datetime.datetime.now().year
                extracted_values = (str(current_year),) + extracted_values  # 年を文字列として追加

            try:
                dt = datetime.datetime(*map(int, extracted_values))
                logger.debug(f"parse_datetime_from_html 関数が終了しました。dt={dt}")
                return dt
            except ValueError as e:
                logger.error(f"日付時刻の変換エラー: {e}")
                return None
    logger.warning(f"parse_datetime_from_html 関数は、対応する日付フォーマットを見つけられませんでした。html_snippet={html_snippet[:50]}...")
    return None

def format_datetime(dt):
    """datetimeオブジェクトをフォーマットする"""
    logger.debug(f"format_datetime 関数が呼ばれました。dt={dt}")
    if isinstance(dt, datetime.datetime):
        formatted_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"format_datetime 関数が終了しました。formatted_dt={formatted_dt}")
        return formatted_dt
    logger.debug(f"format_datetime 関数が終了しました。formatted_dt={dt}") #datetimeオブジェクトではない場合のログ
    return dt

def detect_language(text):
    """
    言語を判定する

    Args:
        text: 言語判定対象のテキスト

    Returns:
        str: 判定された言語
    """
    try:
        language_code = detect(text)
        return language_code
    except LangDetectException:
        return None