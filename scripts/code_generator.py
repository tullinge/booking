#to run from right path
import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

import random as random
from components.db import sql_query

temporary_code_list = []
finnished_code_list = ["BEAR", "MINK", "SEAL", "KOKO", "GRIS", "HARE", "JOEY"]


def main(amount_of_codes):
    if amount_of_codes < 36 ** 8:
        for i in range(amount_of_codes - 7):
            temporary_code_list.append(generate_uuid())
        for code in temporary_code_list:
            if not code in finnished_code_list:
                finnished_code_list.append(code)
                sql_query(f"INSERT INTO `students` (`password`) VALUES ({code});")

def generate_uuid():
    random_string = ""
    random_str_seq = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    uuid_format = [8]
    for n in uuid_format:
        for i in range(0, n):
            random_string += str(
                random_str_seq[random.randint(0, len(random_str_seq) - 1)]
            )
    return random_string


main(30)
print(sql_query("SELECT * FROM student"))
