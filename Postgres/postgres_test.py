
import psycopg2

conn = psycopg2.connect (
    host="localhost",
    database="test",
    user="postgres",
    password="123"
)

conn.autocommit = True

def create_staging_table(cur) -> None:
    cur.execute("""
        DROP TABLE IF EXISTS staging_test;
        CREATE UNLOGGED TABLE staging_test (
            id INTEGER,
            name TEXT   
        );
    """)

with conn.cursor() as cur:
    create_staging_table(cur)