import sqlite3
from contextlib import contextmanager
from dataclasses import astuple, fields
from typing import Any, Generator, Sequence, TypeVar

from psycopg import Connection, sql, connection as connection_

from .entites import FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork

EntityClass = TypeVar('EntityClass', FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork)

TABLES_MAPPER = {
    FilmWork: 'film_work',
    Genre: 'genre',
    Person: 'person',
    GenreFilmWork: 'genre_film_work',
    PersonFilmWork: 'person_film_work',
}
DATACLASSES_MAPPER = {
    'film_work': FilmWork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork,
}

@contextmanager
def conn_context(db_path: str) -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except BaseException as e:  # TODO: Find out which exception is expected, refactor
        # TODO: logging
        ...
    finally:
        conn.close()


class SQLiteLoader:
    DB_PATH = 'db.sqlite'

    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def load_data(
        self,
        table_name: str,
        batch: int = 100,
    ) -> Generator[list[EntityClass], None, None]:
        if batch < 1:
            # TODO: log
            raise ValueError(f'Невозможно читать из БД партиями по {batch} элементов')
        with conn_context(self.DB_PATH) as conn:
            curs = conn.cursor()
            try:
                curs.execute(
                    s:=sql.SQL('SELECT * FROM {0};')
                    .format(sql.Identifier(table_name))
                    .as_string(),
                )
            except BaseException as e:
                print(str(e))
                # TODO logging
                ...
            while data := curs.fetchmany(batch):
                result = [DATACLASSES_MAPPER[table_name](**dict(row)) for row in data]
                yield result


class PostgresSaver:
    def __init__(self, pg_conn: connection_):
        self.pg_conn = pg_conn

    def save_all_data(self, data: Sequence[EntityClass]) -> None:
        if len(data) == 0:
            # TODO: логировать, что данных нет
            raise ValueError('Нет данных для сохранения')
        table_name = sql.Identifier(TABLES_MAPPER[type(data[0])])
        column_names = sql.SQL(', ').join([sql.Identifier(field.name) for field in fields(data[0])])
        values_placeholder = sql.SQL(', ').join(sql.Placeholder() * len(fields(data[0])))
        values = [astuple(entity) for entity in data]
        from pprint import pprint
        pprint(values)

        with self.pg_conn.cursor() as cursor:
            cursor.executemany(
                (
                    sql.SQL('INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING')
                    .format(table_name, column_names, values_placeholder)
                ),
                values,
            )
