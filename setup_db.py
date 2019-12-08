import pymysql
import db_config


def create_conn():
    return pymysql.connect(
        host=db_config.DB_Server,
        user=db_config.DB_Username,
        password=db_config.DB_Password,
        db=db_config.DB_Name,
    )


def create_user_table():
    conn = create_conn()
    create_sql_activitys = """
    CREATE TABLE activitys (
        id int(6) NOT NULL AUTO_INCREMENT,
        name varchar(50) NOT NULL,
        spaces varchar(3) NOT NULL,
        PRIMARY KEY (id)
    );
    """
    create_sql_admins = """
        CREATE TABLE admins (
            id int(6) NOT NULL AUTO_INCREMENT,
            name varchar(50) NOT NULL,
            code varchar(16) NOT NULL,
            PRIMARY KEY (id)
        );
    """

    create_sql_students = """
        CREATE TABLE students (
            id int(6) NOT NULL AUTO_INCREMENT,
            code varchar(4) NOT NULL UNIQUE,
            last_name varchar(50) DEFAULT NULL,
            first_name varchar(50) DEFAULT NULL,
            class varchar(10) DEFAULT NULL,
            activity varchar(100) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_sql_activitys, ())
            cursor.execute(create_sql_admins, ())
            cursor.execute(create_sql_students, ())
        conn.commit()
    finally:
        conn.close()

def insert_user_table():
    conn = create_conn()
    insert_sql_activitys ="""
        INSERT INTO `activitys` 
            (`id`, `name`, `spaces`) 
            VALUES
                (1, "Test", "2")
        ;
    """

    insert_sql_admins ="""
        INSERT INTO `admins` 
            (`id`, `name`, `code`) 
            VALUES
                (1, "Dev", "2357"),
                (2, "Christofer", "Hest"),
                (3, "Joakim", "Jock"),
                (4, "Rebecka", "Rebe"),
                (5, "Susanna", "SUSA"),
                (6, "Ak", "AKAK")
        ;
    """

    insert_sql_students ="""
        INSERT INTO `students` 
            (`id`, `code`, `last_name`, `first_name`, `class`) 
            VALUES 
                (1, "BEAR", "Berzins", "Fredrik", "TE18"),
                (2, "MINK", "Blom", "Oskar", "TE18"),
                (3, "SEAL", "Hedlund", "Marcus", "TE18"),
                (4, "KOKO", "Abu Shamleh", "Nora", "TE18"),
                (5, "GRIS", "Terp", "Jonas", "TE18"),
                (6, "HARE", "Kalström", "Linnea", "TE18"),
                (7, "JOEY", "Brandin", "Isabel", "TE18"),
                (8, "AB12", NULL, NULL, NULL)
        ;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql_activitys, ())
            cursor.execute(insert_sql_admins, ())
            cursor.execute(insert_sql_students, ())
        conn.commit()
    finally:
        conn.close()

def get_all_users():
    conn = create_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM  activitys", ())
            res_activitys = cursor.fetchall()
            cursor.execute("SELECT * FROM  admins", ())
            res_admins = cursor.fetchall()
            cursor.execute("SELECT * FROM  students", ())
            res_students = cursor.fetchall()
        return res_activitys ,res_admins ,res_students
    finally:
        conn.close()

if __name__ == "__main__":
    #create_user_table()
    #insert_user_table()
    print(get_all_users())
    #drop_user_table()