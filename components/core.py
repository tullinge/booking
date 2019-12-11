# tullinge/booking
# https://github.com/tullinge/booking

import string
import hashlib
import binascii
import os

from components.db import sql_query


def is_valid_input(input):
    """Returns False if input variable contains invalid characters, True otherwise"""

    # only ascii letters/digits and swedish letters are allowed
    allowed_characters = (
        list(string.ascii_letters)
        + list(string.digits)
        + ["å", "ä", "ö", "Å", "Ä", "Ö"]
    )

    if any(x not in allowed_characters for x in input):
        # means we've found something that is not allowed
        return False

    # means it's all OK
    return True


def is_integer(variable):
    try:
        int(variable)
    except Exception:
        return False

    return True


def calculate_available_spaces(activity_id):
    """Returns integer of available spaces using specified activity_id"""

    activity = sql_query(f"SELECT * FROM activities WHERE id={activity_id}")[0]
    students = sql_query(f"SELECT * FROM students WHERE choosen_activity={activity_id}")

    return activity[2] - len(students)


def hash_password(password):
    # Hash a password for storing

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)

    pwdhash = binascii.hexlify(pwdhash)

    return (salt + pwdhash).decode("ascii")


def verify_password(stored_password, provided_password):
    # Verify a stored password against one provided by user

    salt = stored_password[:64]
    stored_password = stored_password[64:]

    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )

    pwdhash = binascii.hexlify(pwdhash).decode("ascii")

    return pwdhash == stored_password
