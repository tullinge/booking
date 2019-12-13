# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, request, redirect, session

from components.db import sql_query
from components.core import (
    is_valid_input,
    hash_password,
    verify_password,
    calculate_available_spaces,
    is_integer,
)
from components.decorators import admin_required

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

BASEPATH = "/admin"

# ------ login ------
@admin_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    elif request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        # perform validation, login etc...
        if not username or not password:
            return render_template("admin/login.html", fail="Saknar variabler."), 400

        if len(username) >= 255 or len(password) >= 255:
            return render_template("admin/login.html", fail="För lång input."), 400

        if len(password) <= 4:
            return render_template("admin/login.html", fail="För kort lösenord."), 400

        if not is_valid_input(username, allow_punctuation=True):
            return (
                render_template("admin/login.html", fail="Icke tillåtna kaktärer."),
                400,
            )

        admin = sql_query(f"SELECT * FROM admins WHERE username='{username}'")

        if not admin:
            return (
                render_template(
                    "admin/login.html", fail="Fel användarnamn eller lösenord."
                ),
                401,
            )

        # verify password
        if not verify_password(admin[0][3], password):
            return (
                render_template(
                    "admin/login.html", fail="Fel användarnamn eller lösenord."
                ),
                401,
            )

        session["admin_logged_in"] = True
        session["admin_id"] = admin[0][0]

        # if validation has come this far, user should be authenticated
        return redirect(f"{BASEPATH}/")


@admin_routes.route("/logout")
@admin_required
def logout():
    session.pop("admin_logged_in", False)
    session.pop("admin_id", None)

    return redirect(f"{BASEPATH}/login")


# ------ index ------
@admin_routes.route("/")
@admin_required
def index():
    return render_template("admin/index.html")


# ------ activities ------
@admin_routes.route("/activities")
@admin_required
def activities():
    query = sql_query("SELECT * FROM activities")

    activities = []
    for activity in query:
        activities.append((activity, calculate_available_spaces(activity[0])))

    return render_template("admin/activities.html", activities=activities)


# ------ selected activity ------
@admin_routes.route("/activity/<id>", methods=["POST", "GET"])
@admin_required
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
                "errors/custom.html", title="400", message="Activity dose not exist."
            ),
            400,
        )

    # check if activity has questions
    query = sql_query(f"SELECT * FROM questions WHERE activity_id={id}")
    questions = []

    if query:
        # loops query to add each options for questions into list
        for question in query:
            options = sql_query(
                f"SELECT * FROM options WHERE question_id={question[0]}"
            )

            questions.append([question, options])

    if request.method == "GET":
        return render_template(
            "admin/activity.html",
            activity=activity[0],
            questions=questions,
            available_spaces=calculate_available_spaces(id),
        )

    elif request.method == "POST":
        return "work in progress"


# ------ add/remove admin users ------
@admin_routes.route("/users")
@admin_required
def admin_users():
    return render_template("admin/users.html")


# ------ add/remove students ------
@admin_routes.route("/students")
@admin_required
def students():
    return render_template("admin/students.html")


# ------ add/remove school classes ------
@admin_routes.route("/classes")
@admin_required
def school_classes():
    school_classes = sql_query("SELECT * FROM school_classes")

    return render_template("admin/school_classes.html", school_classes=school_classes)
