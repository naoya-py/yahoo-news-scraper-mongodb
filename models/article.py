from pydantic import BaseModel, HttpUrl, validator
from datetime import datetime

class Article(BaseModel):
    url: HttpUrl
    title: str
    content: str
    published_at: datetime
    source: str  # 例: "yahoo"

    @validator("title", "content", pre=True)
    def remove_extra_whitespaces(cls, value):
        """タイトルとコンテンツの余分な空白を削除するバリデータ"""
        if isinstance(value, str):
            value = value.strip()
            value = ' '.join(value.split())  # 連続した空白を1つに
        return value

    @validator("published_at", pre=True)
    def validate_published_at(cls, value):
        if isinstance(value, str):
            try:
                # 既にdatetimeオブジェクトの場合はそのまま返す
                if isinstance(value, datetime):
                    return value
                # 文字列として渡された場合、datetimeオブジェクトに変換
                return datetime.fromisoformat(value.replace("+09:00", ""))
            except ValueError:
                return None # 無効な日付形式の場合はNoneを返す
        return value # datetimeオブジェクトの場合はそのまま返す