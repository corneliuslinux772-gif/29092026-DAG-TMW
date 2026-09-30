
import sqlite3

import psycopg

from src.ingestion.config import (
    POSTGRES_CONFIG, SOURCE_DB, TABLES
)


def get_postgres_connection():
    return psycopg.connect(**POSTGRES_CONFIG)


def get_sqlite_connection():
    return sqlite3.connect(SOURCE_DB)


def create_schemas(conn):
    with conn.cursor() as cursor:
        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS staging;")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

    conn.commit()


def get_columns(sqlite_conn, table):
    cursor = sqlite_conn.execute(f'PRAGMA table_info("{table}")')

    return [
        {
            "name": row[1],
            "type": row[2],
        }
        for row in cursor.fetchall()
    ]


def sqlite_to_postgres_type(sqlite_type):
    sqlite_type = sqlite_type.upper()

    if "INT" in sqlite_type:
        return "BIGINT"

    if "CHAR" in sqlite_type or "CLOB" in sqlite_type or "TEXT" in sqlite_type:
        return "TEXT"

    if "REAL" in sqlite_type or "FLOA" in sqlite_type or "DOUB" in sqlite_type:
        return "DOUBLE PRECISION"

    if "DATE" in sqlite_type or "TIME" in sqlite_type:
        return "TIMESTAMP"

    return "TEXT"


def create_raw_table(pg_conn, sqlite_conn, table):
    columns = get_columns(sqlite_conn, table)

    definitions = ", ".join(
        f'"{column["name"]}" '
        f'{sqlite_to_postgres_type(column["type"])}'
        for column in columns
    )

    with pg_conn.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS raw."{table}";')

        cursor.execute(
            f'''
            CREATE TABLE raw."{table}" (
                {definitions}
            );
            '''
        )


def load_table(pg_conn, sqlite_conn, table):
    columns = get_columns(sqlite_conn, table)

    column_names = ", ".join(
        f'"{column["name"]}"'
        for column in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    rows = sqlite_conn.execute(
        f'SELECT * FROM "{table}"'
    ).fetchall()

    with pg_conn.cursor() as cursor:
        cursor.executemany(
            f'''
            INSERT INTO raw."{table}"
            ({column_names})
            VALUES ({placeholders});
            ''',
            rows,
        )

    return len(rows)


def main():
    print("Starting RAW ingestion...")

    sqlite_conn = get_sqlite_connection()

    try:
        with get_postgres_connection() as pg_conn:
            create_schemas(pg_conn)

            for table in TABLES:
                print(f"Loading: {table}")

                create_raw_table(
                    pg_conn,
                    sqlite_conn,
                    table,
                )

                row_count = load_table(
                    pg_conn,
                    sqlite_conn,
                    table,
                )

                print(f"  rows: {row_count}")

            pg_conn.commit()

    finally:
        sqlite_conn.close()

    print("RAW ingestion: SUCCESS")


def load_raw(source_db):
    print("Starting RAW ingestion...")

    sqlite_conn = sqlite3.connect(source_db)

    try:
        with get_postgres_connection() as pg_conn:
            create_schemas(pg_conn)

            for table in TABLES:
                print(f"Loading: {table}")

                create_raw_table(
                    pg_conn,
                    sqlite_conn,
                    table,
                )

                row_count = load_table(
                    pg_conn,
                    sqlite_conn,
                    table,
                )

                print(f"  rows: {row_count}")

            pg_conn.commit()

    finally:
        sqlite_conn.close()

    print("RAW ingestion: SUCCESS")


# DEBUG: USED FOR DEV. NOT DELETE IT
# if __name__ == "__main__":
#     main()