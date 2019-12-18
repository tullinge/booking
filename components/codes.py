# tullinge/booking
# https://github.com/tullinge/booking

# imports
# components import
from components.core import random_string
from components.db import sql_query


def generate_code():
    existing_passwords = sql_query("SELECT password FROM school_classes")

    password = random_string(length=8)

    if password not in str(existing_passwords):
        return password

    raise Exception("already exists!")
