import sqlite3
from typing import List


BOOKS = [
    {'id': 0, 'title': 'Война и мир', 'author': 'Лев Толстой'},
    {'id': 1, 'title': 'Мастер и Маргарита', 'author': 'Михаил Булгаков'},
    {'id': 2, 'title': 'Собачье сердце', 'author': 'Михаил Булгаков'},
    {'id': 3, 'title': 'Герой нашего времени', 'author': 'Михаил Лермонтов'},
    {'id': 4, 'title': 'Мертвые души', 'author': 'Николай Гоголь'},
]

class Book:

    def __init__(self, id: int, title: str, author: str):
        self.id = id
        self.title = title
        self.author = author

    def __getitem__(self, item):
        return getattr(self, item)


def init_db(initial_records: List[dict]):
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='table_books';"
        )
        exist = cursor.fetchone()
        if not exist:
            cursor.executescript(
                "CREATE TABLE 'table_books'"
                "(id INTEGER PRIMARY KEY AUTOINCREMENT, title, author)"
            )
            cursor.executemany(
                "INSERT INTO 'table_books'"
                "(title, author) VALUES(?, ?)",
                [(item['title'], item['author']) for item in initial_records]
            )

def get_all_books() -> List[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * from "table_books"')
        all_books = cursor.fetchall()
        return [Book(*row) for row in all_books]



# if __name__ == "__main__":
#     init_db(BOOKS)



















