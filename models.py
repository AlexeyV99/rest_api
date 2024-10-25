import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Union

DATA_BOOKS = [
    {'title': 'Война и мир', 'author': 1},
    {'title': 'Мастер и Маргарита', 'author': 2},
    {'title': 'Собачье сердце', 'author': 2},
    {'title': 'Герой нашего времени', 'author': 3},
]

DATA_AUTHORS = [
    {'first_name': 'Лев', 'last_name': 'Толстой', 'middle_name': 'Николавевич'},
    {'first_name': 'Михаил', 'last_name': 'Булгаков', 'middle_name': ''},
    {'first_name': 'Михаил', 'last_name': 'Лермонтов', 'middle_name': 'Юрьевич'},
]

BOOKS_TABLE_NAME = 'books'
AUTHORS_TABLE_NAME = 'authors'


@dataclass
class Author:
    # id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    id: Optional[int] = None

    def __getitem__(self, item):
        return getattr(self, item)

@dataclass
class Book:
    title: str
    author: int = None
    id: Optional[int] = None

    def __getitem__(self, item):
        return getattr(self, item)

def init_db():
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()

        # таблица авторов
        cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{AUTHORS_TABLE_NAME}';"
        )
        exist = cursor.fetchone()
        if not exist:
            cursor.executescript(
                f"""
                CREATE TABLE '{AUTHORS_TABLE_NAME}'(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    middle_name TEXT NOT NULL DEFAULT ''
                );
                """
            )
            cursor.executemany(
                f"INSERT INTO '{AUTHORS_TABLE_NAME}'"
                "(first_name, last_name, middle_name) VALUES(?, ?, ?)",
                [(item['first_name'], item['last_name'], item['middle_name']) for item in DATA_AUTHORS]
            )

        # таблица книг
        cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{BOOKS_TABLE_NAME}';"
        )
        exist = cursor.fetchone()
        if not exist:
            cursor.executescript('PRAGMA foreign_keys = ON;')
            cursor.executescript(
                f"""
                CREATE TABLE '{BOOKS_TABLE_NAME}'(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author INTEGER NOT NULL,
                    FOREIGN KEY (author) REFERENCES {AUTHORS_TABLE_NAME}(id) ON DELETE CASCADE
                );
                """)
            cursor.executemany(
                f"INSERT INTO '{BOOKS_TABLE_NAME}' (title, author) "
                f"VALUES(?, ?)",
                # f"VALUES(?, (SELECT id FROM {AUTHORS_TABLE_NAME} WHERE id = ?))",
                [(item['title'], item['author']) for item in DATA_BOOKS])

def _get_book_obj_from_row(row) -> Book:
    return Book(id=row[0], title=row[1], author=Author(id=row[2], first_name=row[3], last_name=row[4],
                middle_name=row[5]))
    # return Book(id=row[0], title=row[1], author=Author(first_name=row[2], last_name=row[3], middle_name=row[3]))

def _get_author_obj_from_row(row) -> Author:
    return Author(id=row[0], first_name=row[1], last_name=row[2], middle_name=row[3])

def get_all_books() -> List[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
                        SELECT b.id, b.title, a.id, a.first_name, a.last_name, a.middle_name
                        FROM '{BOOKS_TABLE_NAME}' b
                        JOIN '{AUTHORS_TABLE_NAME}' a
                        ON b.author = a.id 
                        """)
        all_items = cursor.fetchall()
        return [_get_book_obj_from_row(row) for row in all_items]

def get_all_authors() -> List[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * from "{AUTHORS_TABLE_NAME}"')
        all_items = cursor.fetchall()
        return [_get_author_obj_from_row(row) for row in all_items]

def add_book(book: Book) -> Book:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO '{BOOKS_TABLE_NAME}'
            (title, author) VALUES (?, ?)
            """,
            (book.title, book.author)
        )
        book.id = cursor.lastrowid
        return book

def add_author(author: Author) -> Author:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO '{AUTHORS_TABLE_NAME}'
            (first_name, last_name, middle_name) VALUES (?, ?, ?)
            """,
            (author.first_name, author.last_name, author.middle_name)
        )
        author.id = cursor.lastrowid
        return author

def get_book_by_id(book_id: int) -> Optional[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
                        SELECT b.id, b.title, a.id, a.first_name, a.last_name, a.middle_name
                        FROM '{BOOKS_TABLE_NAME}' b
                        JOIN '{AUTHORS_TABLE_NAME}' a
                        ON b.author = a.id 
                        WHERE b.id = '%s'
                        """ % book_id)
        book_item = cursor.fetchone()
        if book_item:
            return _get_book_obj_from_row(book_item)

def update_book_by_id(book: Book):
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE {BOOKS_TABLE_NAME}
            SET title = ?,
                author = ?
            WHERE id = ?
            """, (book.title, book.author, book.id)
        )
        conn.commit()

def delete_book_by_id(book_id):
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            DELETE {BOOKS_TABLE_NAME}
            WHERE id = ?
            """, (book_id,)
        )
        conn.commit()

def get_book_by_title(book_title: str) -> Optional[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * from "{BOOKS_TABLE_NAME}" WHERE title = "%s"' % book_title)
        book = cursor.fetchone()
        return book
        # if book:
        #     return _get_book_obj_from_row(book)

    # with sqlite3.connect('table_books.db') as conn:
    #     cursor = conn.cursor()
    #     cursor.execute(f"""
    #                     SELECT b.id, b.title, a.id, a.first_name, a.last_name, a.middle_name
    #                     FROM '{BOOKS_TABLE_NAME}' b
    #                     JOIN '{AUTHORS_TABLE_NAME}' a
    #                     ON b.author = a.id
    #                     WHERE b.title = "%s"
    #                     """ % book_title)
    #     book = cursor.fetchone()
    #     if book:
    #         return _get_book_obj_from_row(book)

def get_author_by_name(author: dict) -> Optional[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * from "{AUTHORS_TABLE_NAME}" '
                       f'WHERE first_name = ? AND last_name = ?',
                       (author['first_name'], author['last_name']))
        author = cursor.fetchone()
        if author:
            return _get_author_obj_from_row(author)

def get_author_by_id(auth_id: int) -> Optional[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * from "{AUTHORS_TABLE_NAME}" WHERE id = "%s"' % auth_id)
        author = cursor.fetchone()
        if author:
            return _get_author_obj_from_row(author)





