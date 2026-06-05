#Выбор таблицы


sql_genres = "SELECT category_id, name FROM category ORDER BY name"


sql_years  = "SELECT MIN(release_year), MAX(release_year) FROM film"

keyword_count = """
    SELECT COUNT(DISTINCT f.film_id) as movies_count
    FROM film f
    WHERE f.title LIKE %s
    """

keyword_data = """
    SELECT f.film_id, f.title, f.release_year, f.description,f.rating,
           GROUP_CONCAT(c.name ORDER BY c.name SEPARATOR ', ') AS genres
    FROM film f
    LEFT JOIN film_category fc ON f.film_id = fc.film_id
    LEFT JOIN category      c  ON fc.category_id = c.category_id
    WHERE f.title LIKE %s
    GROUP BY f.film_id, f.title, f.release_year, f.description,f.rating
    ORDER BY f.title
    LIMIT %s OFFSET %s
"""


count_genre_only = """
    SELECT COUNT(DISTINCT f.film_id)
    FROM film f
    JOIN film_category fc ON f.film_id = fc.film_id
    WHERE fc.category_id = %s
"""

movies_genre_only = """
    SELECT f.film_id, f.title, f.release_year, f.description, f.rating,
           GROUP_CONCAT(c2.name ORDER BY c2.name SEPARATOR ', ') AS genres
    FROM film f
    JOIN film_category fc  ON f.film_id = fc.film_id
    LEFT JOIN film_category fc2 ON f.film_id = fc2.film_id
    LEFT JOIN category      c2  ON fc2.category_id = c2.category_id
    WHERE fc.category_id = %s
    GROUP BY f.film_id, f.title, f.release_year, f.description, f.rating
    ORDER BY f.release_year, f.title
    LIMIT %s OFFSET %s
"""

count_year_only = """
    SELECT COUNT(DISTINCT f.film_id)
    FROM film f
    WHERE f.release_year BETWEEN %s AND %s
"""

movies_year_only = """
    SELECT f.film_id, f.title, f.release_year, f.description, f.rating,
           GROUP_CONCAT(c.name ORDER BY c.name SEPARATOR ', ') AS genres
    FROM film f
    LEFT JOIN film_category fc ON f.film_id = fc.film_id
    LEFT JOIN category      c  ON fc.category_id = c.category_id
    WHERE f.release_year BETWEEN %s AND %s
    GROUP BY f.film_id, f.title, f.release_year, f.description, f.rating
    ORDER BY f.release_year, f.title
    LIMIT %s OFFSET %s
"""