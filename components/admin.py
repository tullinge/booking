# tullinge/booking
# https://github.com/tullinge/booking

from components.db import sql_query
from components.core import calculate_available_spaces


def get_activites_with_spaces():
    query = sql_query("SELECT * FROM activities")

    activities = []
    for activity in query:
        activities.append((activity, calculate_available_spaces(activity[0])))

    return activities


def get_activity_questions_and_options(id):
    # check if activity has questions
    query = sql_query(
        f"SELECT id, question, written_answer FROM questions WHERE activity_id={id}"
    )
    questions = []

    if query:
        # loops query to add each options for questions into list
        for question in query:
            options = sql_query(
                f"SELECT * FROM options WHERE question_id={question[0]}"
            )

            questions.append([question, options])

    return questions
