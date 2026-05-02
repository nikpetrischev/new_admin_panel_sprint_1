import sqlite3

import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row

from sqlite_to_postgres.log_config import logger
from sqlite_to_postgres.services import PostgresSaver, SQLiteLoader


DB_TABLES = ('film_work', 'person', 'genre', 'person_film_work', 'genre_film_work')


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    for table in DB_TABLES:
        logger.info(msg=f'Обработка таблицы {table}')
        for batch in sqlite_loader.load_data(table):
            postgres_saver.save_all_data(batch)


if __name__ == '__main__':
    logger.info(msg='===== Начало ETL процесса =====')
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
        **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
    logger.info(msg='===== Окончание ETL процесса =====')
