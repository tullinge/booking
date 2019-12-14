# tullinge/booking
# https://github.com/tullinge/booking

import random
import string
import itertools


from components.core import random_string
from components.db import sql_query

# def generate_codes(amount_of_codes):
#     usebel_password_list = ["BESTBEAR", "SMOLMINK", "SEAL"]
#     if int(amount_of_codes) < 36 ** 8 - 1000:
#         for n in range((int(amount_of_codes) - 3)):
#             new_password = ""
#             allowed_caracter = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#             legnth_of_code = 8
#             for i in range(legnth_of_code):
#                 new_password += str(
#                     allowed_caracter[random.randint(0, len(allowed_caracter) - 1)]
#                 )
#             if not new_password in usebel_password_list:
#                 usebel_password_list.append(new_password)
#         for usable_password in usebel_password_list:
#             sql_query(
#                 f"""INSERT INTO `students` (`password`) VALUES ("{usable_password}");"""
#             )


def generate_codes(amount_of_codes):
    new_passwords = []

    for _ in itertools.repeat(None, int(amount_of_codes)):
        password = random_string(length=8)

        sql_query(f"INSERT INTO students (password) VALUES ('{password}')")
        new_passwords.append(password)

    return new_passwords


def reset_students():
    sql_query("""DELETE FROM students;""")
    sql_query("""ALTER TABLE students AUTO_INCREMENT = 1""")
