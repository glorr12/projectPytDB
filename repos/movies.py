from database.sql_client import MySQLConnection
from database.queries import *

page_size = 10

class MoviesDB:
    """Репозиторий для работы с данными о фильмах
    каждый публичный метод открывает
    новое соединение, выполняет запрос и автоматически закрывает соединение
    через контекстный менеджер"""

    sql_genres = sql_genres
    sql_years = sql_years
    keyword_count = keyword_count
    keyword_data = keyword_data

    page_size = 10


    def __init__(self,db_config: dict):
        self._config = db_config

    def _query(self,sql: str, params: tuple = None) -> list:
        """Выполняет запрос с необязательными параметрами и возвращает все строки"""

        with MySQLConnection(self._config) as conn:
            return conn.execute(sql, params)

    def get_genres(self) -> list[dict]:
        """Возвращает все доступные категории по жанрам"""
        return self._query(self.sql_genres)


    def get_year_range(self) -> tuple[int,int]:
        """Возвращает самый ранник и самый поздний год фильма в базе"""
        result = self._query(self.sql_years)
        row = result[0]
        return int(row['MIN(release_year)']), int(row['MAX(release_year)'])

    def count_by_keyword(self, keyword: str) -> int:
        """Считает колличество фильмов , в название которых встречаются ключевые слова"""
        pattern = f"%{keyword}%"
        result = self._query(keyword_count, (pattern,))
        return list(result[0].values())[0]

    def search_keyword(self,keyword: str, limit: int = page_size, offset: int = 0) -> list[dict]:
        """Получает одну страницу фильмов которые соответсвуют ключевому слову"""
        pattern = f"%{keyword}%"
        return self._query(keyword_data, (pattern,limit,offset))

    def paginate_keyword(self,keyword: str):
        """Последовательно выводит страницы с фильмами , которые соответсвуют ключевому слову
        Каждая иттерация возвращает только одну страницу до тех пор , пока не переберутся все
        совпадающие записи"""

        total = self.count_by_keyword(keyword)
        offset = 0
        while offset < total:
            page = self.search_keyword(keyword,page_size,offset)
            yield page
            offset += page_size



    def count_by_genre(self, genre_id: int) -> int:
        """Подсчитывает фильмы , который относяться к жанру"""

        result = self._query(count_genre_only, (genre_id,))
        return list(result[0].values())[0]

    def search_genre(self, genre_id: int, limit: int = page_size, offset: int = 0) -> list[dict]:
        """Получает одну страницу фильмов относящихся к жанру ,который запросил пользователь"""
        return self._query(movies_genre_only, (genre_id, limit, offset))

    def paginate_genre_only(self, genre_id: int):
        """Переход на следующую страницу при поиске по id жанра"""
        total = self.count_by_genre(genre_id)
        offset = 0
        while offset < total:
            yield self.search_genre(genre_id, page_size, offset)
            offset += page_size


    def count_by_year(self, year_from: int, year_to: int) -> int:
        """Поиск фильмов по диапазону определенных лет"""

        result = self._query(count_year_only, (year_from, year_to))
        return list(result[0].values())[0]

    def search_year(self, year_from: int, year_to: int, limit: int = page_size, offset: int = 0) -> list[dict]:
        """Получает отдну страницу фильмов вышедших в диапазоне лет указанном пользователем"""
        return self._query(movies_year_only, (year_from, year_to, limit, offset))

    def paginate_year(self, year_from: int, year_to: int):
        """Последующие выводы страниц диапазона лет запрашивающиеся пользователем"""
        total = self.count_by_year(year_from, year_to)
        offset = 0
        while offset < total:
            yield self.search_year(year_from, year_to, page_size, offset)
            offset += page_size