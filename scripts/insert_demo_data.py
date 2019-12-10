import sys

sys.path.append("../")

from components.db import sql_query

def add_students():
    sql_query(
        """
            INSERT INTO `students` (`id`, `password`) 
                VALUES
                    (1, "DEVBEAR1"),
                    (2, "DevBear2")
            ;
        """
    )

def add_school_classes():
    sql_query(
        """
            INSERT INTO `school_classes` (`id`, `class_name`) 
                VALUES
                    (1, "BET"),
                    (2, "EK17A")
            ;
        """
    )

def add_activities():
    sql_query(
        """
            INSERT INTO `activities` (`id`, `name`, `spaces`) 
                VALUES
                    (1, "Test", 1),
                    (2, "Test2", 2)
            ;
        """
    )

add_students()
add_school_classes()
add_activities()
