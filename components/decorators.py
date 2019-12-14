# tullinge/booking
# https://github.com/tullinge/booking

from functools import wraps
from flask import session, redirect

from components.db import sql_query


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if user is logged in
        if not session.get("logged_in"):
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check if user is logged in
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        # check if user exists aswell
        if not sql_query(f"SELECT id FROM admins WHERE id={session.get('admin_id')}"):
            session.pop("admin_logged_in", False)
            session.pop("admin_id", None)

            return redirect("/admin/login")

        return f(*args, **kwargs)

    return decorated_function


def user_setup_completed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # decorator should be after @login_required, therefore assume user auth
        student = sql_query(f"SELECT * FROM students WHERE id={session.get('id')}")[
            0
        ]  # 0 is the first element of list

        if student:
            if (
                not student[2] or not student[3] or not student[4]
            ):  # checks if user-configurable variables are defined
                # redirect to initial setup page
                return redirect("/setup")
        else:
            # raise exception, should not occur if authentication has succeeded
            raise Exception("user id does not exist")

        return f(*args, **kwargs)

    return decorated_function


def user_not_setup(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # decorator should be after @login_required, therefore assume user auth
        student = sql_query(f"SELECT * FROM students WHERE id={session.get('id')}")[
            0
        ]  # 0 is the first element of list

        if student:
            if student[2] and student[3] and student[4]:
                # user has already configured
                return redirect("/")
        else:
            # raise exception, should not occur if authentication has succeeded
            raise Exception("user id does not exist")

        return f(*args, **kwargs)

    return decorated_function
