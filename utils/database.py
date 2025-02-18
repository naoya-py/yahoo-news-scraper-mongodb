import os
import atexit
from pymongo import MongoClient, ReturnDocument, ASCENDING
from config import MONGODB_URI, MONGODB_DB
from loggings.logger import get_logger
from typing import Union
from models.article import Article

logger = get_logger(__name__)
_client = None


def get_database():
    """MongoDBに接続し、データベースを返す"""
    global _client
    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI, maxPoolSize=50, minPoolSize=5, maxIdleTimeMS=300000)
            logger.info("MongoDB に接続しました。")

            # インデックスを作成
            db = _client[MONGODB_DB]
            collection_name = os.environ.get("MONGODB_COLLECTION")  # 環境変数から取得

            if not collection_name:  # 環境変数が設定されていない場合のエラー処理
                raise ValueError("MONGODB_COLLECTION 環境変数が設定されていません。")

            collection = db[collection_name]
            collection.create_index([("url", ASCENDING)], unique=True, background=True)
            logger.info(f"URLのユニークインデックスを作成しました。(collection: {collection_name})")

        except Exception as e:
            logger.error(f"MongoDB への接続、またはインデックスの作成に失敗しました: {e}")
            raise  # 例外を再送出

    try:
        return _client[MONGODB_DB]
    except Exception as e:
        logger.error(f"データベースの取得に失敗しました: {e}")
        raise


def save_data(data: Union[Article, dict], collection_name: str = os.environ.get("MONGODB_COLLECTION")):
    """データをMongoDBに保存する

    Args:
        data: 保存するデータ (Articleオブジェクトまたは辞書)
        collection_name: コレクション名

    Returns:
        bool: True if successful, False otherwise.
    """
    db = get_database()

    if not collection_name:
        raise ValueError("MONGODB_COLLECTION 環境変数が設定されていません。")
    try:
        collection = db[collection_name]

        if isinstance(data, Article):
            data_dict = data.model_dump()
            data_dict['url'] = str(data_dict['url']) #url を文字列に変換
        elif isinstance(data, dict):
            data_dict = data
        else:
            logger.error(f"無効なデータ型: {type(data)}")
            return False

        result = collection.insert_one(data_dict)
        logger.info(f"データが保存されました。collection={collection_name}, inserted_id={result.inserted_id}")
        return True

    except Exception as e:
        logger.error(f"データの保存に失敗しました: {e}")
        return False


def update_data(filter_query: dict, update_data: dict, collection_name: str = os.environ.get("MONGODB_COLLECTION"), upsert: bool = False):
    """データを更新する

    Args:
        collection_name: コレクション名
        filter_query: 更新対象を絞り込むためのクエリ (辞書)
        update_data: 更新内容 (辞書)。`$set` 演算子などを使用する。
        upsert: True に設定すると、更新対象が存在しない場合に新規作成する。

    Returns:
        UpdateResult | None: 更新結果。失敗時は None。
    """
    db = get_database()
    if not collection_name:
        raise ValueError("MONGODB_COLLECTION 環境変数が設定されていません。")

    collection = db[collection_name]

    try:
        result = collection.update_one(filter_query, update_data, upsert=upsert)
        logger.info(
            f"データが更新されました。collection={collection_name}, matched_count={result.matched_count}, modified_count={result.modified_count}, upserted_id={result.upserted_id}")
        return result
    except Exception as e:
        logger.error(f"データの更新に失敗しました: {e}")
        return None


def delete_data(filter_query: dict, collection_name: str = os.environ.get("MONGODB_COLLECTION")):
    """データを削除する

    Args:
        collection_name: コレクション名
        filter_query: 削除対象を絞り込むためのクエリ (辞書)

    Returns:
        DeleteResult | None: 削除結果。失敗時は None。
    """
    db = get_database()

    if not collection_name:
        raise ValueError("MONGODB_COLLECTION 環境変数が設定されていません。")
    collection = db[collection_name]

    try:
        result = collection.delete_many(filter_query)
        logger.info(f"データが削除されました。collection={collection_name}, deleted_count={result.deleted_count}")
        return result
    except Exception as e:
        logger.error(f"データの削除に失敗しました: {e}")
        return None


def close_mongodb_connection():
    """MongoDB 接続を閉じる"""
    global _client
    if _client:
        _client.close()
        logger.info("MongoDB 接続を閉じました。")


atexit.register(close_mongodb_connection)