# tullinge/booking
# https://github.com/tullinge/booking

import random
import string

from components.core import random_string
from components.db import sql_query

def generate_codes(amount_of_codes):
    new_passwords = []

    while int(amount_of_codes) == len(new_passwords):
        password = random_string(length=8)

        if not password in new_passwords:
            sql_query(f"INSERT INTO students (password) VALUES ('{password}')")
            new_passwords.append(password)

    return new_passwords


def reset_students():
    sql_query("""DELETE FROM students;""")
    sql_query("""DELETE FROM answers;""")
    sql_query("""ALTER TABLE students AUTO_INCREMENT = 1""")
    