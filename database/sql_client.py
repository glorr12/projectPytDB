import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'host': os.getenv('SQL_HOST'),
    'user': os.getenv('SQL_USER'),
    'password': os.getenv('SQL_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'cursorclass': pymysql.cursors.DictCursor
}


class MySQLConnection:
    """    Открывает новое соединение и курсор `DictCursor` в `__enter__`,
    а затем закрывает оба в `__exit__`  независимо от того,
    возникло исключение или нет"""

    def __init__(self, db_config: dict):
        self.__config = db_config
        self.__conn = None
        self.__cursor = None

    def __enter__(self):
        """Установливает соединение с базой данных и открывает `DictCursor`"""

        self.__conn = pymysql.connect(**self.__config)
        self.__cursor = self.__conn.cursor(pymysql.cursors.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрывает курсор и соединение"""

        if self.__cursor:
            self.__cursor.close()
        if self.__conn:
            self.__conn.close()
        return False


    @staticmethod
    def _validator(params):
        """Проверяет аргумент *params* перед передачей в курсор"""

        if params is None:
            return None
        if not isinstance(params, (tuple, list, dict)):
            raise TypeError("неверный тип данных")
        return params

    def execute(self, sql: str, params: tuple = None) -> list:
        """Выполняет SQL-запрос и возвращает все строки результата"""

        params = self._validator(params)
        self.__cursor.execute(sql, params)
        return self.__cursor.fetchall()
