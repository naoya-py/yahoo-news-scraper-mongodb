from utils.data_converter import convert_to_csv
from scrapers.yahoo_news.yahoo_news import scrape_yahoo_news
from loggings.logger import get_logger

logger = get_logger(__name__)

def main():
    """スクレイピングを実行し、結果をCSVファイルに保存する"""

    try:
        scraped_data = scrape_yahoo_news()  # scrape_yahoo_news関数を修正
        if scraped_data:
            convert_to_csv(scraped_data, 'yahoo_news.csv')
        else:
            logger.warning("スクレイピング結果が空です。CSVファイルは作成されません。")
    except Exception as e:
        logger.error(f"メイン処理でエラー発生: {e}")


if __name__ == "__main__":
    main()