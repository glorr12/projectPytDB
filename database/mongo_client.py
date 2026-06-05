import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

class MongoConnection:
    """Контекстный менеджер для работы с клиентом PyMongo
        предназначен для использования в блоке `with` соединение
    гарантированно закрывается при выходе из блока, даже если
    возникло исключение """

    def __init__(self,config: str, db_name: str):
        self.__config = config
        self.__db_name = db_name
        self.__client = None
        self.db = None


    def __enter__(self):
        """Открыть соединение с клиентом и выбирает базу данных"""

        self._client = MongoClient(self.__config)
        self.db = self._client[self.__db_name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает соединение при выходе из блока `with`"""

        if self.__client:
            self.__client.close()


    def get_collection(self, collection_name: str):
        """ Возвращает объект коллекции PyMongo по имени"""
        
        if self.db is not None:
            return self.db[collection_name]
        raise ConnectionError("Соединение с MongoDB не установлено.")

    def insert_one(self,collection_name: str, document: dict):
        """Вставляет один документ в указанную коллекцию"""
        
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)



    def get_top_queries(self, collection_name: str, limit: int = 5) -> list:
        """Агрегация наиболее частых выполняемых запросов"""
        if self.db is None:
            raise ConnectionError("Соединение с MongoDB не установлено.")

        cfg = [
            {
                "$group": {
                    "_id": {"query_type": "$query_type", "params": "$params"},
                    "count": {"$sum": 1},
                    "last_used": {"$max": "$timestamp"}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "query_type": "$_id.query_type",
                    "params": "$_id.params",
                    "count": 1,
                    "last_used": 1
                }
            }
        ]
        return list(self.db[collection_name].aggregate(cfg))