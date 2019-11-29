import pymysql
from student import dconfig

def _create_conn():
    return pymysql.connect(
        host=dconfig.DB_Server,
        user=dconfig.DB_Username,
        password=dconfig.DB_Password,
        db=dconfig.DB_Name
    )

def create_user_table():
    conn = _create_conn()

    create_sql = '''CREATE TABLE users (
        id INT NOT NULL AUTO_INCREMENT,
        email VARCHAR(64),
        name VARCHAR(64),
        PRIMARY KEY (id)
    )'''

    insert_sql = 'INSERT INTO `users` (`email`, `name`) VALUES (%s, %s)'

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_sql, ())
            cursor.execute(insert_sql, ('mike@tyson.com', 'Mike'))
        conn.commit()
    finally:
        conn.close()

def drop_user_table():
    conn = _create_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DROP TABLE users', ())
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    drop_user_table()
    create_user_table()
