"""models module"""

from pony.orm import Database, Optional, Required, Set

db = Database()


class User(db.Entity):
    """User table"""
    _table_ = 'User'
    name = Required(str)
    todos = Set('Todo')


class Todo(db.Entity):
    """To do table"""
    _table_ = 'Todo'
    name = Required(str)

    user = Optional(User)


db.bind(provider='sqlite', filename='demo.db', create_db=True)
db.generate_mapping(create_tables=True)
