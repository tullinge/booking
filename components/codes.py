# tullinge/booking
# https://github.com/tullinge/booking

import random
import string

from components.core import random_string
from components.db import sql_query


def generate_codes(amount_of_codes):
    new_passwords = []
    existing_passwords = sql_query("SELECT password FROM students")

    while int(amount_of_codes) != len(new_passwords):
        password = random_string(length=8)

        if not password in new_passwords and password not in existing_passwords:
            sql_query(f"INSERT INTO students (password) VALUES ('{password}')")
            new_passwords.append(password)

    return new_passwords
