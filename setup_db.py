from components.db import sql_query
    
sql_query("""
    CREATE TABLE activities (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(50) NOT NULL,
        spaces VARCHAR(3) NOT NULL,
        PRIMARY KEY (id)
    );
""")
    
sql_query("""
    CREATE TABLE admins (
        id INT NOT NULL AUTO_INCREMENT,
        name VARCHAR(50) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
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

sql_query("""
    INSERT INTO `activities` 
        (`id`, `name`, `spaces`) 
        VALUES
            (1, "Test", "2")
    ;
""")

sql_query("""
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
""")

sql_query("""
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
""")


print(sql_query("""
    SELECT * FROM  activities;
"""))

print(sql_query("""
    SELECT * FROM  admins;
"""))

print(sql_query("""
    SELECT * FROM  students;
"""))