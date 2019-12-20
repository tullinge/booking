# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import session

# components import
from components.db import dict_sql_query


def student_chosen_activity():
    """Returns dict of chosen activity, if student has chosen"""

    student = dict_sql_query(
        f"SELECT * FROM students WHERE id={session.get('id')}", fetchone=True
    )

    return (
        dict_sql_query(
            f"SELECT * FROM activities WHERE id={student['chosen_activity']}",
            fetchone=True,
        )
        if student["chosen_activity"]
        else None
    )
