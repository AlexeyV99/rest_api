from typing import List, Dict
from flask import Flask, render_template
from models import get_all_books, Book

app = Flask(__name__)

BOOKS = [
    {'id': 0, 'title': 'Война и мир', 'author': 'Лев Толстой'},
    {'id': 1, 'title': 'Мастер и Маргарита', 'author': 'Михаил Булгаков'},
    {'id': 2, 'title': 'Собачье сердце', 'author': 'Михаил Булгаков'},
    {'id': 3, 'title': 'Герой нашего времени', 'author': 'Михаил Лермонтов'},
    {'id': 4, 'title': 'Мертвые души', 'author': 'Николай Гоголь'},
]

def _get_html_table_for_books(books: List[Book]) -> str:
    table = """
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Author</th>
                </tr>
            </thead>
            <tbody>
                {books_rows}
            </tbody>
        </table>
    """

    rows = ''
    for book in books:
        rows += '<tr><td>{id}</td><td>{title}</td><td>{author}</td>'.format(
            id=book['id'], title=book['title'], author=book['author'],
        )
    return table.format(books_rows=rows)


@app.route('/books')
def all_books() -> str:
    # return render_template('index.html', tables=_get_html_table_for_books(get_all_books()))
    return render_template('index.html', books=get_all_books())


@app.route('/books/form')
def get_books_form():
    return render_template('add_book.html')

if __name__ == "__main__":
    app.run(debug=True)
