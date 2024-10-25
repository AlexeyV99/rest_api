from dataclasses import asdict
from typing import List, Dict, Tuple
import os

from aniso8601 import parse_time
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from marshmallow import ValidationError
from flasgger import APISpec, Swagger
from apispec_webframeworks.flask import FlaskPlugin
from models import get_all_books, get_all_authors, init_db, add_book, add_author, get_book_by_id
from schemas import BookSchema, AuthorSchema, BookListSchema, BookEditSchema

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
                $ref: '#/definitions/Book'
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
                $ref: '#/definitions/Book'
        """
        data = request.json
        schema_book = BookSchema()
        try:
            book = schema_book.load(data, many=False)
        except ValidationError as exc:
            return exc.messages, 400
        book = add_book(book)
        schema_book_info = BookListSchema()
        print(book)
        return schema_book_info.dump(get_book_by_id(book.id)), 201

class AuthorsResource(Resource):

    def get(self) -> Tuple[List[Dict], int]:
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
                $ref: '#/definitions/Book'
        """
        schema_author = AuthorSchema()
        return schema_author.dump(get_all_authors(), many=True), 200

    def post(self) -> Tuple[Dict, int]:
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
                $ref: '#/definitions/Book'
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
    def get(self, book_id) -> tuple[list[dict], int]:
        schema = BookListSchema()
        res = get_book_by_id(book_id)
        if res:
            return schema.dump(res), 200
        # else:
        #     raise ValidationError(f'Книги с id="{book_id}" не существует в базе данных')
        # try:
        #     return schema.dump(get_book_by_id(book_id)), 200
        # except ValidationError as exc:
        #     return exc.messages, 400



template = spec.to_flasgger(
    app,
    definitions=[BookSchema],
)

swagger = Swagger(app, template_file='swagger.json')

api.add_resource(BooksResource, '/api/books')
api.add_resource(BooksEdit, '/api/books/<int:book_id>')
api.add_resource(AuthorsResource, '/api/authors')
# api.add_resource(AuthorsEdit, '/api/authors/<int: id>')


if __name__ == "__main__":
    if os.path.exists('table_books.db'):
        os.remove('table_books.db')
    init_db()
    app.run(debug=True)
