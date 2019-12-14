# tullinge/booking
# https://github.com/tullinge/booking

from flask import session

from components.db import sql_query


def student_chosen_activity():
    """Returns boolean based on if student has booked or not and activity object if booked"""

    student = sql_query(f"SELECT * FROM students WHERE id={session.get('id')}")

    activity = None
    status = False
    if student[0][5]:
        activity = sql_query(f"SELECT name FROM activities WHERE id={student[0][5]}")
        status = True

    return status, activity
