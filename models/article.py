from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime
from loggings.logger import get_logger

logger = get_logger(__name__)

class Article(BaseModel):
    url: HttpUrl
    title: str
    content: str
    coment: str
    author: str
    published_at: datetime
    updated_at: datetime
    source: dict

    @validator("title", "content", pre=True)
    def remove_extra_whitespaces(cls, value):
        """タイトルとコンテンツの余分な空白を削除するバリデータ"""
        if isinstance(value, str):
            original_value = value  # オリジナルの値を保存
            value = value.strip()
            value = ' '.join(value.split())
            if original_value != value:  # 変更があった場合のみログ出力
                logger.debug(f"remove_extra_whitespaces: '{original_value[:50]}...' を '{value[:50]}...' に変更しました")
        return value

    @validator("published_at", pre=True)
    def validate_published_at(cls, value):
        """published_atを検証・変換するバリデータ"""
        if isinstance(value, str):
            try:
                if isinstance(value, datetime):
                    return value  # 既にdatetimeオブジェクトの場合そのまま返す
                converted_value = datetime.fromisoformat(value.replace("+09:00", ""))
                logger.debug(f"validate_published_at: '{value}' を '{converted_value}' に変換しました") #変換後の値をログ出力
                return converted_value
            except ValueError:
                logger.warning(f"validate_published_at: 無効な日付形式: {value}")
                return None
        elif not isinstance(value, datetime): # datetimeオブジェクトでない場合のログを追加
            logger.warning(f"validate_published_at: datetimeオブジェクトではありません: {value}")
            return None
        return value
