# tullinge/booking
# https://github.com/tullinge/booking

from functools import wraps
from flask import session, redirect


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if user is logged in
        if not session.get("logged_in"):
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function
