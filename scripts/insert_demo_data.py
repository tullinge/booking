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
                    (1, "DEV1"),
                    (2, "DEV2")
            ;
        """
    )


def add_activities():
    sql_query(
        """
            INSERT INTO `activities` (`id`, `name`, `spaces`, `info`) 
                VALUES
                    (1, "Demo Activity", 30, "This is a demo activity, added for testing purposes."),
                    (2, "Demo Activity 2", 20, "And this is another one.")
            ;
        """
    )


add_students()
add_school_classes()
add_activities()
