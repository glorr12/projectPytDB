import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_CONFIG = os.getenv("client")
MONGO_NAME = os.getenv("result")

class MongoConnection:
    def __init__(self,config_dict: dict, db_name: str):
        self.__config = config_dict
        self.__db_name = db_name
        self.__client = None
        self.db = None


    def __enter__(self):
        self.__client = MongoClient(**self.__config)
        self.db = self.__client[self.__db_name]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__client:
            self.__client.close()
        return False

    def insert_one(self,collection_name: str, document: dict):
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)