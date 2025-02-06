from fake_useragent import UserAgent
from loggings.logger import get_logger  # logger.py からロガーを取得

logger = get_logger(__name__)  # ロガーを取得
ua = UserAgent(os='windows')


def get_random_user_agent():
    """
    ランダムなUser-Agentを生成する

    Returns:
        str: ランダムなUser-Agent文字列。UserAgentの取得に失敗した場合はNoneを返す。
    """
    try:
        user_agent = ua.random
        logger.debug(f"Generated User-Agent: {user_agent}")  # debugログに変更
        return user_agent
    except Exception as e:
        logger.error(f"User-Agentの取得に失敗しました: {e}")  # エラーログを出力
        return None