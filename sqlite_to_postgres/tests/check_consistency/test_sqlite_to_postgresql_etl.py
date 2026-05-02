"""
Набор базовых тестов для проверки корректности выполнения ETL процесса.
В дальнейшем стоит пеервести на pytest и добавить в CI/CD.
"""

from dataclasses import asdict
from datetime import datetime
import logging
import sqlite3

import psycopg
from psycopg import ClientCursor, sql
from psycopg.rows import dict_row

from contextlib import closing, contextmanager

from sqlite_to_postgres.entites import FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork
from sqlite_to_postgres.log_config import logger


DB_TABLES = ('film_work', 'person', 'genre', 'person_film_work', 'genre_film_work')
BATCH_SIZE = 100
DATACLASSES_MAPPER = {
    'film_work': FilmWork,
    'genre': Genre,
    'person': Person,
    'genre_film_work': GenreFilmWork,
    'person_film_work': PersonFilmWork,
}


def test_identical_number_of_rows(sqlite_curs, pg_curs):
    """
    Положительный тест на соответствие кол-ва строк записей
    в таблицах SQLite3 и Postgresql.
    """

    sqlite_row_count = {}
    pg_row_count = {}

    for table_name in DB_TABLES:
        query = (
            sql.SQL('SELECT COUNT(*) FROM {0};')
            .format(sql.Identifier(table_name))
            .as_string()
        )
        sqlite_curs.execute(query)
        sqlite_row_count[table_name] = sqlite_curs.fetchone()[0]
        pg_curs.execute(query)
        pg_row_count[table_name] = pg_curs.fetchone()['count']

    assert sqlite_row_count == pg_row_count, 'Кол-во рядов в таблицах не совпадает!'


def test_row_data_consistency(sqlite_curs, pg_curs):
    """
    Положительный тест на соответствие содержимого записей
    в таблицах SQLite3 и Postgresql.
    """

    for table_name in DB_TABLES:
        sqlite_query = (
            sql.SQL('SELECT * FROM {};')
            .format(sql.Identifier(table_name))
            .as_string()
        )
        sqlite_curs.execute(sqlite_query)
        while batch := sqlite_curs.fetchmany(BATCH_SIZE):
            print(batch)
            id_values = [item['id'] for item in batch]
            placeholders = sql.SQL(', ').join(sql.Placeholder() * len(id_values))
            pg_query = (
                sql.SQL('SELECT * FROM {} WHERE id IN ({});')
                .format(sql.Identifier(table_name), placeholders)
                .as_string()
            )
            pg_curs.execute(pg_query, id_values)
            pg_res = pg_curs.fetchall()
            sqlite_res = [dict(item) for item in batch]
            sqlite_entities = {}
            pg_entities = {}
            for i in range(len(sqlite_res)):
                sqlite_res[i]['created_at'] = datetime.fromisoformat(sqlite_res[i]['created_at'])
                if sqlite_res[i].get('updated_at'):
                    sqlite_res[i]['updated_at'] = datetime.fromisoformat(sqlite_res[i]['updated_at'])
                if sqlite_res[i].get('creation_date'):
                    sqlite_res[i]['creation_date'] = datetime.fromisoformat(sqlite_res[i]['creation_date'])
                sqlite_enity = asdict(DATACLASSES_MAPPER[table_name](**sqlite_res[i]))
                sqlite_entities[sqlite_enity['id']] = sqlite_enity
                pg_entities[pg_res[i]['id']] = asdict(DATACLASSES_MAPPER[table_name](**pg_res[i]))

            assert sqlite_entities == pg_entities, (
                'Данные в соответствующих таблицах SQLite3 и Postgresql не идентичны!',
            )


@contextmanager
def stream_warning():
    """
    Контекстный менеджер для мьюта логгера на уровне INFO
    на время прохождения тестов.
    """

    sh = next(
        h for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
    )
    old_logger_level = logger.level
    old_sh_level = sh.level

    logger.setLevel(logging.WARNING)
    sh.setLevel(logging.WARNING)
    try:
        yield
    finally:
        sh.setLevel(old_sh_level)
        logger.setLevel(old_logger_level)


def run_tests(sqlite_conn, pg_conn):
    """Временный раннер для тестов до встройки их в CI/CD."""

    with (
        closing(sqlite_conn.cursor()) as sqlite_curs,
        closing(pg_conn.cursor(row_factory=dict_row)) as pg_curs,
    ):
        try:
            test_identical_number_of_rows(sqlite_curs, pg_curs)
            test_row_data_consistency(sqlite_curs, pg_curs)
        except AssertionError as e:
            logger.error(msg=f'Тестирование выявило следующую ошибку:\n\t"{e}"')
            logger.warning(msg='===== Ошбика при переносе данных =====')
        else:
            logger.warning(msg='===== Данные были перенесены корректно =====')


if __name__ == '__main__':
    """Старт тестов в отрыве от самого ETL процессса."""

    from sqlite_to_postgres.load_data import load_from_sqlite

    logger.warning(msg='===== Проверка корректности переноса данных =====')
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with (
        closing(sqlite3.connect('db.sqlite')) as sqlite_conn,
        closing(psycopg.connect(
            **dsl,
            row_factory=dict_row,
            cursor_factory=ClientCursor,
        )) as pg_conn,
        stream_warning(),
    ):
        sqlite_conn.row_factory = sqlite3.Row
        load_from_sqlite(sqlite_conn, pg_conn)
        pg_conn.commit()

        run_tests(sqlite_conn, pg_conn)
