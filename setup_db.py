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
    create_sql_activitys = """CREATE TABLE activitys (ID int(3) NOT NULL,Name varchar(50) NOT NULL,Spaces varchar(3) NOT NULL);"""
    create_sql_admins = """CREATE TABLE admins (ID int(2) NOT NULL,Name varchar(50) NOT NULL,Code varchar(16) NOT NULL);"""
    create_sql_students = """CREATE TABLE students (ID int(6) NOT NULL AUTO_INCREMENT,Code varchar(4) NOT NULL,LastName varchar(50) DEFAULT NULL,FirstName varchar(50) DEFAULT NULL,Class varchar(10) DEFAULT NULL,activity varchar(100) DEFAULT NULL,PRIMARY KEY (ID),UNIQUE KEY Code (Code));"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_sql_activitys, ())
            cursor.execute(create_sql_admins, ())
            cursor.execute(create_sql_students, ())
        conn.commit()
    finally:
        conn.close()

def alter_user_table():
    conn = create_conn()
    alter_sql_activitys = """ALTER TABLE `activitys` ADD PRIMARY KEY (`ID`);"""
    alter_sql_admins = """ALTER TABLE `admins` ADD PRIMARY KEY (`ID`);"""
    alter_sql_students = """ALTER TABLE `students` ADD PRIMARY KEY (`ID`), ADD UNIQUE KEY `Code` (`Code`);"""

    try:
        with conn.cursor() as cursor:
            cursor.execute(alter_sql_activitys, ())
            cursor.execute(alter_sql_admins, ())
            cursor.execute(alter_sql_students, ())
        conn.commit()
    finally:
        conn.close()

def insert_user_table():
    conn = create_conn()
    insert_sql_activitys ="""INSERT INTO `activitys` (`Name`, `Spaces`) VALUES('Test', '2');"""
    insert_sql_admins ="""INSERT INTO `admins` (`Name`, `Code`) VALUES('Dev', '2357'),('Christofer', 'Hest'),('Joakim', 'Jock'),('Rebecka', 'Rebe'),('Susanna', 'SUSA'),('Ak', 'AKAK');"""
    insert_sql_students ="""INSERT INTO `students` (`Code`, `LastName`, `FirstName`, `Class`, `activity`) VALUES ("BEAR", "Berzins", "Fredrik", "TE18", NULL);"""

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
            cursor.execute("SELECT * FROM  admins", ())
            cursor.execute("SELECT * FROM  students", ())
            res = cursor.fetchall()
        return res
    finally:
        conn.close()

if __name__ == "__main__":
    create_user_table()
    alter_user_table()
    insert_user_table()
    print(get_all_users())
    #drop_user_table()