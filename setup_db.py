# tullinge/booking
# https://github.com/tullinge/booking

from components.db import sql_query

# create tables
def create_tabels():
    # activities
    sql_query(
        """
        CREATE TABLE activities (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) DEFAULT NULL,
            spaces INT DEFAULT NULL,
            info VARCHAR(511) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """
    )

    # questions
    sql_query(
        """
        CREATE TABLE questions (
            id INT NOT NULL AUTO_INCREMENT,
            activity_id INT NOT NULL,
            question VARCHAR(255) NOT NULL,
            written_answer BOOLEAN DEFAULT FALSE,
            PRIMARY KEY (id)
        );
    """
    )

    # options on questions
    sql_query(
        """
        CREATE TABLE options (
            id INT NOT NULL AUTO_INCREMENT,
            question_id INT NOT NULL,
            text VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        );
    """
    )

    # answers from students
    sql_query(
        """
        CREATE TABLE answers (
            id INT NOT NULL AUTO_INCREMENT,
            question_id INT NOT NULL,
            option_id INT DEFAULT NULL,
            written_answer VARCHAR(255) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """
    )

    # admins
    # password should always be stored in hashed format
    sql_query(
        """
        CREATE TABLE admins (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) DEFAULT NULL,
            username VARCHAR(255) DEFAULT NULL,
            password VARCHAR(255) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """
    )

    # students
    # password is stored in plain text
    sql_query(
        """
        CREATE TABLE students (
            id INT NOT NULL AUTO_INCREMENT,
            password VARCHAR(8) NOT NULL UNIQUE,
            last_name VARCHAR(50) DEFAULT NULL,
            first_name VARCHAR(50) DEFAULT NULL,
            class VARCHAR(10) DEFAULT NULL,
            choosen_activity INT DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """
    )

    # school_classes
    sql_query(
        """
        CREATE TABLE school_classes (
            id INT NOT NULL AUTO_INCREMENT,
            class_name VARCHAR(10) NOT NULL UNIQUE,
            PRIMARY KEY (id)
        );
    """
    )

if __name__ == "__main__":
    create_tabels()
