import pymysql
import db_config


def _create_conn():
    return pymysql.connect(
        host=db_config.DB_Server,
        user=db_config.DB_Username,
        password=db_config.DB_Password,
        db=db_config.DB_Name,
    )


def create_user_table():
    conn = _create_conn()

    create_sql = """CREATE TABLE users (
        id INT NOT NULL AUTO_INCREMENT,
        email VARCHAR(64),
        name VARCHAR(64),
        PRIMARY KEY (id)
    )"""

    insert_sql = "INSERT INTO `users` (`email`, `name`) VALUES (%s, %s)"

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_sql, ())
            cursor.execute(insert_sql, ("mike@tyson.com", "Mike"))
        conn.commit()
    finally:
        conn.close()


def drop_user_table():
    conn = _create_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE users", ())
        conn.commit()
    finally:
        conn.close()

def get_all_users():
    conn = _create_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM  users", ())
            res = cursor.fetchall()
        return res
    finally:
        conn.close()

if __name__ == "__main__":
    print(get_all_users())
    #drop_user_table()
    #create_user_table()
