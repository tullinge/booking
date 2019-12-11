# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import Blueprint, render_template, redirect, request, session

# components import
from components.core import is_valid_input, is_integer
from components.decorators import login_required, user_setup_completed, user_not_setup
from components.db import sql_query

# blueprint init
student_routes = Blueprint("student_routes", __name__, template_folder="../templates")


@student_routes.route("/")
@login_required
@user_setup_completed
def index():
    activities = sql_query("SELECT * FROM activities")

    return render_template(
        "student/index.html",
        fullname=session.get("fullname"),
        school_class=session.get("school_class"),
        activities=activities,
    )


@student_routes.route("/login", methods=["GET", "POST"])
def students_login():
    if request.method == "GET":
        return render_template("student/login.html")
    else:
        password = request.form["password"]

        if not password:
            return render_template("student/login.html", fail="Saknar lösenord."), 400

        if not len(password) == 8:
            return render_template("student/login.html", fail="Fel längd."), 400

        if not is_valid_input(password):
            return (
                render_template(
                    "student/login.html",
                    fail="Icke tillåtna kaktärer. Endast alfabetet och siffror tillåts.",
                ),
                400,
            )

        # authentication
        student = sql_query(
            f"SELECT * FROM `students` WHERE `password` = BINARY '{password}'"
        )

        if not student:
            return render_template(
                "student/login.html", fail="Användaren existerar inte/fel lösenord."
            )

        # means user is authentication
        session["id"] = student[0][0]
        session["logged_in"] = True

        # try to set fullname if user has already configured
        student = student[0]

        if student[2] and student[3]:
            session["fullname"] = f"{student[3]} {student[2]}"

        if student[4]:
            session["school_class"] = student[4]

        # if come this far, we'll redirect to the /setup page
        return redirect("/setup")


@student_routes.route("/logout")
@login_required
def logout():
    session.pop("logged_in", False)
    session.pop("id", None)

    return redirect("/login")


@student_routes.route("/setup", methods=["POST", "GET"])
@login_required
@user_not_setup
def setup():
    school_classes = sql_query("SELECT * FROM school_classes")

    if request.method == "GET":
        return render_template("student/setup.html", school_classes=school_classes)
    elif request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        school_class = request.form["class"]

        # all input variables need to be present
        if not first_name or not last_name or not school_class:
            return render_template(
                "student/setup.html",
                school_classes=school_classes,
                fail="Saknar variabler.",
            )

        # make sure to validate input variables against string authentication
        if (
            not is_valid_input(first_name)
            or not is_valid_input(last_name)
            or not is_valid_input(school_class)
        ):
            return render_template(
                "student/setup.html",
                school_classes=school_classes,
                fail="Icke tillåtna karaktärer. Endast alfabetet och siffror tillåts.",
            )

        # verify that the school_class provided by the user actually is valid
        if school_class not in str(
            school_classes
        ):  # poorly validated, but should be sufficient
            return render_template(
                "student/setup.html",
                school_classes=school_classes,
                fail="Angiven skolklass existerar inte.",
            )

        # passed validation, update user variables
        sql_query(
            f"UPDATE students SET first_name = '{first_name}', last_name = '{last_name}', class = '{school_class}' WHERE id={session['id']}"
        )

        # if above fails, would raise exception
        session["fullname"] = f"{first_name} {last_name}"
        session["school_class"] = school_class

        # redirect to index
        return redirect("/")


@student_routes.route("/activity/<id>")
@login_required
@user_setup_completed
def selected_activity(id):
    if not is_integer(id):
        return (
            render_template(
                "errors/custom.html", title="400", message="ID is not integer."
            ),
            400,
        )

    activity = sql_query(f"SELECT * FROM activities WHERE id={id}")

    if not activity:
        return (
            render_template(
                "errors/custom.html", title="400", message="Activity is not integer."
            ),
            400,
        )

    return render_template(
        "student/activity.html",
        activity=activity[0],
        fullname=session.get("fullname"),
        school_class=session.get("school_class"),
    )


@student_routes.route("/confirmation")
@login_required
@user_setup_completed
def confirmation():
    activity = sql_query(f"SELECT * FROM activities WHERE id={id}")

    return render_template(
        "student/confirmation.html",
        activity=activity[0],
        fullname=session.get("fullname"),
        school_class=session.get("school_class"),
    )
