import sys
from dotenv import load_dotenv
from ui import MovieSearchUI


def main() -> None:
    load_dotenv()

    try:
        ui = MovieSearchUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n Работа программы прервана пользователем ")
        sys.exit(0)
    except Exception as e:
        print(f"\nКритическая ошибка при работе приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()