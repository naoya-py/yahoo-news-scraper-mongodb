import re
import html
import unicodedata
from bs4 import BeautifulSoup
import datetime
import MeCab
import csv
from loggings.logger import get_logger
import pandas as pd
import csv
import re

mecab = MeCab.Tagger("-Ochasen")
logger = get_logger(__name__)

# 感情語辞書の読み込み
with open('pn.csv.m3.120408.trim', 'r', encoding='utf-8') as infile, open('cleaned.csv', 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile, delimiter='\t') # 一旦タブ区切りで読み込み
    writer = csv.writer(outfile, delimiter='\t')

    for row in reader:
        try:
            new_row = [re.sub(r'[^\x00-\x7F\u3000-\u30FF\u4E00-\u9FFF\uF900-\uFAFF\uFF01-\uFF5E]+', '', cell) for cell in row[:2]] # 不正な文字を削除し、2列目まで取得
            if all(new_row): # 空のセルがないことを確認
                writer.writerow(new_row)
        except Exception as e:
            print(f"Error processing row: {row}, Error: {e}")

df_dic = pd.read_csv('cleaned.csv', sep='\t', names=("名詞", "判定"), encoding='utf-8')

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
    formats = [
        r"(\d+)/(\d+)\(.+?\)\s*(\d+):(\d+)",  # "2/2(日) 20:15"
        r"(\d+)年(\d+)月(\d+)日(\d+)時(\d+)分",  # "2025年2月4日19時35分"
    ]
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
    # TODO: NLTKを使って言語判定を実装
    pass


def analyze_sentiment(text):
    """
    感情分析を行う

    Args:
        text: 感情分析対象のテキスト

    Returns:
        dict: 感情分析結果。辞書が見つからない場合はNoneを返す。
    """
    logger.debug(f"analyze_sentiment 関数が呼ばれました。text={text[:50]}...")
    if not df_dic:  # 辞書が空の場合
        logger.debug(f"analyze_sentiment 関数が終了しました。result=None")
        return None

    node = mecab.parseToNode(text)
    score = 0
    while node:
        word = node.surface
        if word in df_dic:
            score += df_dic[word]
        node = node.next

    # スコアに基づいて感情を判定。しきい値は調整可能。
    if score > 0.5:
        sentiment = "positive"
    elif score < -0.5:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    result = {"sentiment": sentiment, "score": score}
    logger.debug(f"analyze_sentiment 関数が終了しました。result={result}")
    return result