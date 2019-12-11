# tullinge/booking
# https://github.com/tullinge/booking

from os import environ
import pymysql


def create_conn():
    """
    Creates a connection from environment variables (or developer defaults if missing)
    """
    return pymysql.connect(
        host=environ.get("MYSQL_HOST", "localhost"),
        user=environ.get("MYSQL_USER", "admin"),
        password=environ.get("MYSQL_PASSWORD", "do-not-use-in-production"),
        db=environ.get("MYSQL_DATABASE", "booking"),
    )


def sql_query(query):
    """
    Performs specified SQL query in database. Returns result from cursor.fetchall(), usually tuple
    If searching for a specific object, note that object will be wrapped in outside tuple
    """

    conn = create_conn()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        conn.commit()
    finally:
        conn.close()

    return result
