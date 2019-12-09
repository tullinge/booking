# tullinge/booking
# https://github.com/tullinge/booking

import pymysql
from db_config import DB_Name, DB_Password, DB_Server, DB_Username


def create_conn():
    return pymysql.connect(
        host=DB_Server, user=DB_Username, password=DB_Password, db=DB_Name,
    )


def sql_query(query):
    conn = create_conn()

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        conn.commit()
    finally:
        conn.close()

    return result
