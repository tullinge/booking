# tullinge/booking
# https://github.com/tullinge/booking

import string
import hashlib
import binascii
import os
import random

from flask import request

from components.db import sql_query

def basic_validation(expected_values):
    """
    Basic input/form validation, checks if all expected values are present

    :param expected_values, list of values that should be defined
    """

    if len(request.form) != len(expected_values):
        return False

    for v in expected_values:
        if not request.form.get(v):
            return False

    return True

#calculats avalebel spaces foo activitys
def calculate_available_spaces(
    activity_id
):
    """Returns integer of available spaces using specified activity_id"""

    activity = sql_query(f"SELECT * FROM activities WHERE id={activity_id}")[0]
    students = sql_query(f"SELECT * FROM students WHERE chosen_activity={activity_id}")

    return activity[2] - len(students)

#Hash a password for storing
def hash_password(
    password
):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)

    pwdhash = binascii.hexlify(pwdhash)

    return (salt + pwdhash).decode("ascii")

#verifys a hashed password
def verify_password(
    stored_password, provided_password
):
    # Verify a stored password against one provided by user

    salt = stored_password[:64]
    stored_password = stored_password[64:]

    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )

    pwdhash = binascii.hexlify(pwdhash).decode("ascii")

    return pwdhash == stored_password

#gives out a random string of ccaracters
def random_string(
    length=10
):
    """Generate a random string of fixed length"""

    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for i in range(length)
    )


def get_client_ip():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        remote_ip = request.environ["REMOTE_ADDR"]
    else:
        remote_ip = request.environ["HTTP_X_FORWARDED_FOR"]

    return remote_ip

#full validations of strings
def valid_input (
    variable, min_length, max_length, allow_space=True, allow_punctuation=True, swedish=True, allow_newline=True
):

    """Returns boolean whether variable is valid input or not"""
    if not variable:
        return False
    if max_length == False and not min_length <= len(variable):
        return False

    elif not min_length <= len(variable) <= max_length:
        return False

    ILLEGAL_CHARACTERS = ["<", ">", ";"]
    ALLOWED_CHARACTERS = list(string.ascii_letters) + list(string.digits)

    if allow_space:
        ALLOWED_CHARACTERS.extend(list(string.whitespace))

    if not allow_newline:
        try:
            ALLOWED_CHARACTERS.remove("\n")
        except Exception:
            pass

    if allow_punctuation:
        ALLOWED_CHARACTERS.extend(list(string.punctuation))

    if swedish:
        ALLOWED_CHARACTERS.extend(["å", "ä", "ö", "Å", "Ä", "Ö"])

    if any(x in variable for x in ILLEGAL_CHARACTERS):
        return False

    if any(x not in ALLOWED_CHARACTERS for x in variable):
        return False

    return True

#   validation for integers
def is_integer(
    variable
):
    try:
        int(variable)
    except Exception:
        return False

    return True

def valid_integer(
    variable, min_length, max_length
):  
    if max_length == False and not min_length <= len(variable):
        return False
    else:
        if not min_length <= len(variable) <= max_length:
            return False

    try:
        int(variable)
    except Exception:
        return False

    return True