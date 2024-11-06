from typing import Optional
from marshmallow import validates, post_load, pre_load
from models import get_book_by_title, Book, Author, get_author_by_id, get_author_by_name, get_book_by_id
from flasgger import Schema, ValidationError, fields


class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    middle_name = fields.Str()

    @validates('first_name')
    def validate_first_name(self, first_name: str) -> None:
        if not first_name:
            raise ValidationError('! Проверьте имя автора')

    @validates('last_name')
    def validate_last_name(self, last_name: str) -> None:
        if not last_name:
            raise ValidationError('! Проверьте фамилию автора')

    # @validates('id')
    # def validate_id(self, id: int) -> Union[None, ValidationError]:
    #     if not id:
    #         raise ValidationError('! Ошибка ID автора')

    @post_load
    def create_author(self, data, **kwargs) -> Author:
        return Author(**data)

    @pre_load
    def pre_create_author(self, data, **kwargs):
        if get_author_by_name(data):
            raise ValidationError('Такой автор уже есть в базе')
        else:
            return data

class BookSchema(Schema):

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Int(required=True)
    # author = fields.Nested(AuthorSchema(), required=True)

    # @validates('title')
    # def validate_title(self, title: str) -> None:
    #     if get_book_by_title(title):
    #         raise ValidationError("Книга с названием '{title}' уже существует".format(title=title))

    @validates('author')
    def validate_author(self, author: Optional[int]) -> None:
        if isinstance(author, int):
            if not get_author_by_id(author):
                raise ValidationError(f'Автора с таким id={author} не существует')
        elif isinstance(author, dict):
            if not author.get('first_name'):
                raise ValidationError(f'Введите в запросе имя автора (first_name)')
        else:
            raise ValidationError(f'Неправильный тип данных автора')


    @pre_load
    def pre_create_book(self, data, **kwargs) -> Book:
        if isinstance(data['author'], int):
            auth = get_author_by_id(data['author'])
            if not auth:
                raise ValidationError(f'Нет автора с таким id={data['author']}!')
        elif isinstance(data['author'], dict):
            if not data['author'].get('first_name') or not data['author'].get('last_name'):
                raise ValidationError(f'Введите в запросе имя и фамилию автора (first_name, last_name)')
            else:
                auth = get_author_by_name(data['author'])
                if auth:
                    data['author'] = auth.id
                else:
                    raise ValidationError(f'Нет автора с таким именем и фамилией, '
                                          f'сначала надо добавить его в таблицу авторов!')
        else:
            raise ValidationError(f'Неправильный тип данных автора')
        return data

    @post_load
    def post_create_book(self, data, **kwargs) -> Book:
        return Book(**data)

class BookListSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Nested(AuthorSchema(), required=True)
    # book_id = fields.Int(required=False)

    # @validates('book_id')
    # def validate_book_id(self, book_id: int) -> None:
    #     print(book_id)
    #     if not get_book_by_id(book_id):
    #         raise ValidationError(f'Нет книги с таким id={book_id}')

# class BookEditSchema(Schema):
#     id = fields.Int(required=True)
#
#     @validates('id')
#     def validate_book_id(self, id: int) -> None:
#         if not get_book_by_id(id):
#             raise ValidationError(f'Нет книги с таким id={id}')

