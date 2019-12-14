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
