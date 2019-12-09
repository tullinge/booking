# tullinge/booking
# https://github.com/tullinge/booking

from components.db import sql_query

#----------CREATE----------
def create_tabels():
    sql_query("""
        CREATE TABLE activities (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) DEFAULT NULL,
            spaces VARCHAR(3) DEFAULT NULL,
            info VARCHAR(511) DEFAULT NULL,
            extra BOOLEAN DEFAULT FALSE,
            yesorno BOOLEAN DEFAULT FALSE,
            question VARCHAR(50) DEFAULT NULL,
            answeryesorno BOOLEAN DEFAULT NULL,
            answer VARCHAR(255) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """)
        
    sql_query("""
        CREATE TABLE admins (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(50) DEFAULT NULL,
            username VARCHAR(255) DEFAULT NULL,
            password VARCHAR(255) DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """)

    sql_query("""
        CREATE TABLE students (
            id INT NOT NULL AUTO_INCREMENT,
            password VARCHAR(4) NOT NULL UNIQUE,
            last_name VARCHAR(50) DEFAULT NULL,
            first_name VARCHAR(50) DEFAULT NULL,
            class VARCHAR(10) DEFAULT NULL,
            choosen_activity INT DEFAULT NULL,
            PRIMARY KEY (id)
        );
    """)
#----------INSERT----------
def insert_into_tabels():
    sql_query("""
        INSERT INTO `activities` 
            (`id`, `name`, `spaces`) 
            VALUES
                (1, "Test", "2")
        ;
    """)

    sql_query("""
        INSERT INTO `admins` 
            (`id`, `username`, `password`) 
            VALUES
                (1, "dev", "2357"),
                (2, "christofer", "HEST"),
                (3, "joakim", "JOCK"),
                (4, "rebecka", "REBE"),
                (5, "susanna", "SUSA"),
                (6, "ak", "AKAK")
        ;
    """)

    sql_query("""
        INSERT INTO `students` 
            (`id`, `password`, `last_name`, `first_name`, `class`) 
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
    """)
#----------PRINT----------
def print_tabels():
    print(sql_query("""
        SELECT * FROM  activities;
    """))

    print(sql_query("""
        SELECT * FROM  admins;
    """))

    print(sql_query("""
        SELECT * FROM  students;
    """))

create_tabels()
insert_into_tabels()
print_tabels()