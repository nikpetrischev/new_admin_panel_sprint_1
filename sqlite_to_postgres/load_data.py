import os
import sqlite3
from contextlib import closing
from pathlib import Path

import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row
from dotenv import load_dotenv

from sqlite_to_postgres.log_config import logger
from sqlite_to_postgres.services import PostgresSaver, SQLiteLoader
from sqlite_to_postgres.tests.check_consistency.test_sqlite_to_postgresql_etl import run_tests


DB_TABLES = ('film_work', 'person', 'genre', 'person_film_work', 'genre_film_work')

DOTENV_PATH = Path(__file__).resolve().parent.parent / 'movies_admin' / '.env'
load_dotenv(dotenv_path=DOTENV_PATH)


def load_from_sqlite(sql_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres."""

    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(sql_conn)

    for table in DB_TABLES:
        logger.info(msg=f'Обработка таблицы {table}')
        for batch in sqlite_loader.load_data(table):
            postgres_saver.save_all_data(batch)


if __name__ == '__main__':
    logger.info(msg='===== Начало ETL процесса =====')
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5432),
    }
    with (
        closing(sqlite3.connect('db.sqlite')) as sqlite_conn,
        closing(psycopg.connect(
            **dsl,
            row_factory=dict_row,
            cursor_factory=ClientCursor,
        )) as pg_conn,
    ):
        sqlite_conn.row_factory = sqlite3.Row
        load_from_sqlite(sqlite_conn, pg_conn)
        pg_conn.commit()

        run_tests(sqlite_conn, pg_conn)

    logger.info(msg='===== Окончание ETL процесса =====')
