# tullinge/booking
# https://github.com/tullinge/booking

import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from components.db import sql_query

# To add info to most databases for development purposes


def add_students():
    sql_query(
        """
            INSERT INTO `students` (`password`)
                VALUES
                    ("DEVBEAR1"),
                    ("DevBear2")
            ;
        """
    )


def add_school_classes():
    sql_query(
        """
            INSERT INTO `school_classes` (`class_name`)
                VALUES
                    ("DEV1"),
                    ("DEV2")
            ;
        """
    )


def add_activities():
    sql_query(
        """
            INSERT INTO `activities` (`name`, `spaces`, `info`)
                VALUES
                    ("Demo Activity", 30, "This is a demo activity, added for testing purposes."),
                    ("Demo Activity 2", 20, "And this is another one.")
            ;
        """
    )


def add_questions_options():
    sql_query(
        """
            INSERT INTO `questions` (`activity_id`, `question`, `written_answer`)
            VALUES
                (1, "Are you ready?", 0),
                (1, "Written answer question", 1)
            ;
        """
    )

    sql_query(
        """
            INSERT INTO `options` (`question_id`, `text`)
            VALUES
                (1, "Yes!"),
                (1, "No!")
            ;
        """
    )


add_students()
add_school_classes()
add_activities()
add_questions_options()
