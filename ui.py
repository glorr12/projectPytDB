from datetime import datetime
from repos.movies import MoviesDB, page_size
from database.sql_client import config as mysql_config
from database.mongo_client import MongoConnection, MONGO_URL, MONGO_DATABASE, MONGO_COLLECTION


class MovieSearchUI:
    """Треминальный интерфейс поиска фильмов
    Присутсвуют константы разделителя для заголовка и между записями"""

    FIRST_DIVIDER  = "=" * 60
    SECOND_DIVIDER = "─" * 60

    def __init__(self):
        """Инициализация UI """
        self.repo = MoviesDB(mysql_config)

    @staticmethod
    def _log_search(query_type: str, params: dict) -> None:
        """Сохранение логи поиска в MongoDB"""

        try:
            with MongoConnection(MONGO_URL, MONGO_DATABASE) as conn:
                conn.insert_one(MONGO_COLLECTION, {
                    "query_type": query_type,
                    "params":     params,
                    "timestamp":  datetime.now(),
                })
        except Exception as e:
            print(f"Log error: {e}")

    def show_top_searches(self) -> None:
        """Вывод пяти наиболее частых запросов"""

        print(f"\n{self.FIRST_DIVIDER}")
        print(" Top-5 popular queries: ")
        print(self.FIRST_DIVIDER)

        try:
            with MongoConnection(MONGO_URL, MONGO_DATABASE) as conn:
                queries = conn.get_top_queries(MONGO_COLLECTION, limit=5)

            if not queries:
                print("\nQuery list is empty. Try to search some movies")
                return

            print()
            for rank, q in enumerate(queries, start=1):
                ts= q.get("last_used")
                ts_str = ts.strftime("%d.%m.%Y %H:%M") if ts else "—"
                print(f"{rank}. Search type: {q['query_type']}")
                print(f"Number of searches : {q['count']} time(s)")
                print(f"Last query: {ts_str}")

                match q["query_type"]:
                    case "keyword":
                        print(f"Keyword: «{q['params'].get('keyword')}»")
                    case "genre":
                        print(f"Genre: {q['params'].get('genre')}")
                    case "year":
                        print(f"Years: {q['params'].get('from')} – {q['params'].get('to')}")
                print()

        except Exception as e:
            print(f"An error occurred on obtaining statistics: {e}")


    @staticmethod
    def _read_int(prompt: str, error_msg: str, condition=None) -> int:
        """Запрашивает ввод у пользователя до тех пор , пока не будет
        введено корректное число"""

        while True:
            try:
                value = int(input(prompt))
                if condition is None or condition(value):
                    return value
                print(error_msg)
            except ValueError:
                print(error_msg)

    @staticmethod
    def _print_film(film: dict) -> None:
        """Выводит отформатированую информацию о фильме"""

        title  = film.get("title", "—")
        year   = film.get("release_year", "—")
        rating = film.get("rating", "—")
        genres = film.get("genres", "—")

        desc = film.get("description", "")
        if desc and len(desc) > 100:
            desc = desc[:100] + "..."
        if not desc:
            desc = "—"

        print(f"\n  Movie name: {title}")
        print(f"Rating : {rating}")
        print(f"Description : {desc}")
        print(f"Release year: {year}")
        print(f"Genre: {genres}")

    def _show_films(self, pages_generator) -> None:
        """Генератор страниц и отображение результата """

        for page_num, page in enumerate(pages_generator, start=1):
            print(f"\n Page {page_num}:")
            print(self.SECOND_DIVIDER)
            for film in page:
                self._print_film(film)

            if len(page) == page_size:
                while True:
                    answer = input("\n Want to see next 10 pages ? [y/n]: ").strip().lower()
                    if answer == "y":
                        break
                    elif answer == "n":
                        print("\nRequest cancelled by user")
                        return
                    else:
                        print("Type 'y' or 'n'")
            else:
                print("\n That's all results")
                break

    def _pick_genre(self) -> tuple[int, str]:
        """Отображение доступных жанров и предложение пользователю выбрать один по ID"""

        genres = self.repo.get_genres()
        print("\n Available genres:")
        for genre in genres:
            print(f"{genre['category_id']:2d} — {genre['name']}")

        valid_ids  = {g["category_id"] for g in genres}
        genre_id   = self._read_int(
            prompt="\nSelect genre ID: ",
            error_msg="Incorrect ID. Chose number from list",
            condition=lambda v: v in valid_ids,
        )
        genre_name = next(g["name"] for g in genres if g["category_id"] == genre_id)
        return genre_id, genre_name

    def _pick_year_range(self) -> tuple[int, int]:
        """Отображение доступного диапазона лет и предложение пользователю
        ввестьи диапазон начального и конечного года"""

        min_y, max_y = self.repo.get_year_range()
        print(f"\nYears available: {min_y} – {max_y}")

        year_from = self._read_int(
            prompt=f"\nFrom {min_y}: ",
            error_msg=f"Write down year from {min_y} to {max_y}.",
            condition=lambda v: min_y <= v <= max_y,
        )
        year_to = self._read_int(
            prompt=f"to {max_y}: ",
            error_msg=f"Write down year to {max_y}.",
            condition=lambda v: year_from <= v <= max_y,
        )
        return year_from, year_to


    def search_by_keyword(self) -> None:
        """Запуск поиска по ключевому слову"""

        print(f"\n{self.FIRST_DIVIDER}")
        print(" Search by the movie name")
        print(self.FIRST_DIVIDER)

        keyword = input("\nWrite down key word: ").strip()
        if not keyword:
            print("Empty input")
            return

        total = self.repo.count_by_keyword(keyword)
        print(f"\nMovies found: {total}")
        if total == 0:
            print("Nothing has been found")
            return

        self._log_search("keyword", {"keyword": keyword})
        self._show_films(self.repo.paginate_keyword(keyword))

    def search_by_genre(self) -> None:
        """Запускает поиск по жанру"""

        print(f"\n{self.FIRST_DIVIDER}")
        print("Search by genre")
        print(self.FIRST_DIVIDER)

        genre_id, genre_name = self._pick_genre()

        total = self.repo.count_by_genre(genre_id)
        print(f"\n Founded movies: {total}")
        if total == 0:
            print("Nothing has been found")
            return

        self._log_search("genre", {"genre": genre_name})
        self._show_films(self.repo.paginate_genre_only(genre_id))

    def search_by_year(self) -> None:
        """Запуск поиска по диапазону лет"""
        print(f"\n{self.FIRST_DIVIDER}")
        print("Search by year")
        print(self.FIRST_DIVIDER)

        year_from, year_to = self._pick_year_range()

        total = self.repo.count_by_year(year_from, year_to)
        print(f"\n Movies found: {total}")
        if total == 0:
            print("Nothing has been found")
            return

        self._log_search("year", {"from": year_from, "to": year_to})
        self._show_films(self.repo.paginate_year(year_from, year_to))


    def run(self) -> None:
        """Запускает основной цикл приложение с отображением главного меню и
        управлением приложения в зависимости от выбора пользователя
        Цикл останавливает только если пользователь нажмёт '0' """
        while True:
            print(f"\n{self.FIRST_DIVIDER}")
            print(" *DUNGEON MASTER AND SLAVES co.* Movie search")
            print(self.FIRST_DIVIDER)
            print("\n1. Search by movie name ")
            print("2. Search by genre")
            print("3. Search by year")
            print("4. Top-5 popular queries")
            print("0. Exit\n")

            match input("Choose and option between [0-4]: ").strip():
                case "0":
                    print("\nCya folks!\n")
                    break
                case "1":
                    self.search_by_keyword()
                case "2":
                    self.search_by_genre()
                case "3":
                    self.search_by_year()
                case "4":
                    self.show_top_searches()
                case _:
                    print("Invalid choice. Please enter a number from 0 to 4")

            input("\nPress 'Enter' to continue")


