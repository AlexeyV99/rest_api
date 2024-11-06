from typing import List, Dict, Tuple
import os
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from flasgger import APISpec, Swagger
from apispec_webframeworks.flask import FlaskPlugin
from models import get_all_books, get_all_authors, init_db, add_book, add_author, get_book_by_id, Book, \
    update_book_by_id, delete_book_by_id, get_author_by_id, Author, delete_author_by_id, update_author_by_id
from schemas import BookSchema, AuthorSchema, BookListSchema


app = Flask(__name__)
api = Api(app)

spec = APISpec(
    title='BooksList',
    version='1.0.0',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)

class BooksResource(Resource):

    def get(self) -> tuple[list[dict], int]:
        """
        This is endpoint for obtaining the books list.
        ---
        tags:
          - books
        responses:
          200:
            description: Books data
            schema:
              type: array
              items:
                $ref: '#/definitions/BookList'
        """
        schema = BookListSchema()
        return schema.dump(get_all_books(), many=True), 200

    def post(self) -> tuple[dict, int]:
        """
        This is endpoint for book creation.
        ---
        tags:
          - books
        parameters:
          - in: body
            name: new book params
            schema:
              $ref: '#/definitions/Book'
        responses:
          201:
            description: The book has been created
            schema:
              items:
                $ref: '#/definitions/BookList'
          400:
            description: Error validation
        """
        data = request.json
        schema_book = BookSchema()
        try:
            book = schema_book.load(data, many=False)
        except ValidationError as exc:
            return exc.messages, 400
        book = add_book(book)
        schema_book_info = BookListSchema()
        return schema_book_info.dump(get_book_by_id(book.id)), 201

class AuthorsResource(Resource):

    def get(self) -> Tuple[List[Dict], int]:
        """
        This is endpoint for obtaining the Authors list.
        ---
        tags:
          - authors
        responses:
          200:
            description: Author data
            schema:
              type: array
              items:
                $ref: '#/definitions/Author'
        """
        schema_author = AuthorSchema()
        return schema_author.dump(get_all_authors(), many=True), 200

    def post(self) -> Tuple[Dict, int]:
        """
        This is endpoint for author creation.
        ---
        tags:
          - authors
        parameters:
          - in: body
            name: new Author params
            schema:
              $ref: '#/definitions/Author'
        responses:
          201:
            description: The Author has been created
            schema:
              items:
                $ref: '#/definitions/Author'
          400:
            description: Error validation
        """
        data = request.json
        schema_author = AuthorSchema()
        try:
            author = schema_author.load(data)
        except ValidationError as exc:
            return exc.messages, 400
        author = add_author(author)
        return schema_author.dump(author), 201

class BooksEdit(Resource):

    def get(self, book_id: int) -> tuple[list[dict], int]:
        """
        This is endpoint to obtain the book info.
        ---
        tags:
          - books
        parameters:
          - in: path
            name: book_id
            type: int
        responses:
          200:
            description: Book data
            schema:
              items:
                $ref: '#/definitions/BookList'
          404:
            description: No such book
        """

        schema = BookListSchema()
        res = get_book_by_id(book_id)
        if res:
            return schema.dump(res), 200
        else:
            return [{"error": f"Книги с таким ID({book_id}) нет"}], 404


        # schema = BookEditSchema()
        # res = {}
        # res['id'] = book_id
        # try:
        #     schema.load(res, many=False)
        # except ValidationError as exc:
        #     return exc.messages, 404
        #
        # schema = BookListSchema()
        # res = get_book_by_id(book_id)
        # return schema.dump(res), 200

    def put(self, book_id: int) -> tuple[dict, int]:
        """
        This is endpoint to update the book info.
        ---
        tags:
          - books
        parameters:
          - in: path
            name: book_id
            type: int
          - in: body
            name: new book params
            schema:
              $ref: '#/definitions/Book'
        responses:
          200:
            description: Book data
            schema:
              items:
                $ref: '#/definitions/Book'
          400:
            description: Error validation
        """

        data = request.json
        schema_book = BookSchema()
        try:
            schema_book.load(data, many=False)
        except ValidationError as exc:
            return exc.messages, 400


        book = get_book_by_id(book_id)
        book_new = Book(
            title = data['title'],
            author = data['author'],
            id = book['id']
        )

        update_book_by_id(book_new)

        schema_book_info = BookListSchema()
        return schema_book_info.dump(get_book_by_id(book_id)), 200

    def delete(self, book_id: int):
        """
        This is endpoint to delete the book.
        ---
        tags:
          - books
        parameters:
          - in: path
            name: book_id
            type: int
        responses:
          200:
            description: Good result
          404:
            description: No such book
        """
        if get_book_by_id(book_id):
            delete_book_by_id(book_id)
            return [{"info": "Удаление прошло успешно"}], 200
        else:
            return [{"error": "Книги с таким ID нет"}], 404

class AuthorsEdit(Resource):

    def get(self, author_id: int) -> tuple[list[dict], int]:
        """
        This is endpoint to obtain the author info.
        ---
        tags:
          - authors
        parameters:
          - in: path
            name: author_id
            type: int
        responses:
          200:
            description: Author data
            schema:
              items:
                $ref: '#/definitions/Author'
          404:
            description: No such author
        """

        schema = AuthorSchema()
        res = get_author_by_id(author_id)
        if res:
            return schema.dump(res), 200
        else:
            return [{"error": f"Автора с таким ID({author_id}) нет"}], 404


    def put(self, author_id: int) -> tuple[dict, int]:
        """
        This is endpoint to update the author info.
        ---
        tags:
          - authors
        parameters:
          - in: path
            name: author_id
            type: int
          - in: body
            name: new author params
            schema:
              $ref: '#/definitions/Author'
        responses:
          200:
            description: Author data
            schema:
              items:
                $ref: '#/definitions/Author'
          400:
            description: Error validation
        """

        data = request.json
        schema = AuthorSchema()
        try:
            schema.load(data, many=False)
        except ValidationError as exc:
            return exc.messages, 400

        auth = get_author_by_id(author_id)
        author_new = Author(
            first_name = data['first_name'],
            last_name = data['last_name'],
            middle_name = data['middle_name'],
            id = auth['id']
        )

        update_author_by_id(author_new)
        return schema.dump(get_author_by_id(author_id)), 200

    def delete(self, author_id: int):
        """
        This is endpoint for delete the author.
        ---
        tags:
          - authors
        parameters:
          - in: path
            name: author_id
            type: int
        responses:
          200:
            description: Good result
          404:
            description: No such author
        """
        if get_author_by_id(author_id):
            delete_author_by_id(author_id)
            return [{"info": "Удаление прошло успешно"}], 200
        else:
            return [{"error": "Автора с таким ID нет"}], 404


template = spec.to_flasgger(
    app,
    definitions=[AuthorSchema, BookListSchema, BookSchema],
)

swagger = Swagger(app, template=template)

api.add_resource(BooksResource, '/api/books')
api.add_resource(AuthorsResource, '/api/authors')
api.add_resource(BooksEdit, '/api/books/<int:book_id>')
api.add_resource(AuthorsEdit, '/api/authors/<int:author_id>')


if __name__ == "__main__":
    if os.path.exists('table_books.db'):
        os.remove('table_books.db')
    init_db()
    app.run(debug=True)
