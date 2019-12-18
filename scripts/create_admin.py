# tullinge/booking
# https://github.com/tullinge/booking

import sys
from pathlib import Path

# Add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from components.db import sql_query
from components.core import hash_password
from components.validation import valid_string

data = {}

data["name"] = input("Enter name: ")
data["username"] = input("Enter username: ").lower()
data["password"] = input("Enter password: ")

for k, v in data.items():
    if len(v) >= 255 or len(v) < 4:
        raise Exception(f"{k} too long or too short (4-255)")

    if k == "name":
        if not valid_string(v, allow_newline=False, allow_punctuation=False):
            raise Exception("name contains illegal characters")

    if k == "username":
        if not valid_string(
            v,
            allow_space=False,
            swedish=False,
            allow_punctuation=False,
            allow_newline=False,
        ):
            raise Exception("username contains illegal characters")

    if k == "password":
        if len(v) < 8:
            raise Exception("password needs to be at least 8 characters")

sql_query(
    f"INSERT INTO admins (name, username, password) VALUES ('{data['name']}', '{data['username']}', '{hash_password(data['password'])}')"
)
