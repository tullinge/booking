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

    create_sql = """
        CREATE TABLE activitys (ID INT(3) NOT NULL AUTO_INCREMENT,Name varchar(50) NOT NULL,Spaces varchar(3) NOT NULL,PRIMARY KEY (ID)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1; CREATE TABLE admins (ID int(2) NOT NULL AUTO_INCREMENT,Name varchar(50) NOT NULL,Code varchar(16) NOT NULL,PRIMARY KEY (ID)) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=latin1; CREATE TABLE students (ID int(6) NOT NULL AUTO_INCREMENT,Code varchar(4) NOT NULL,LastName varchar(50) DEFAULT NULL,FirstName varchar(50) DEFAULT NULL,Class varchar(10) DEFAULT NULL,activity varchar(100) DEFAULT NULL,PRIMARY KEY (ID),UNIQUE KEY Code (Code)) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
        """

    insert_sql ="""
        INSERT INTO `activitys` (`Name`, `Spaces`) VALUES ("Test", "2"); INSERT INTO `admins` (`Name`, `Code`) VALUES ("Dev", "2357"); INSERT INTO `students` (`Code`, `LastName`, `FirstName`, `Class`, `activity`) VALUES ("BEAR", "Berzins", "Fredrik", "TE18", NULL);
        """

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, ())
            cursor.execute(create_sql, ())
        conn.commit()
    finally:
        conn.close()

def get_all_users():
    conn = create_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM  students", ())
            res = cursor.fetchall()
        return res
    finally:
        conn.close()

if __name__ == "__main__":
    #print(get_all_users())
    #drop_user_table()
    create_user_table()
