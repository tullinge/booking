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
from components.codes import generate_codes

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

BASEPATH = "/admin"

# ------ login ------
@admin_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    elif request.method == "POST":
        username = request.form["username"]
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
    admins = sql_query("SELECT id, name, username FROM admins")

    return render_template("admin/users.html", admins=admins)


# ------ add/remove students ------
@admin_routes.route("/students", methods=["GET", "POST"])
@admin_required
def students():
    students = None
    if request.args.get("show"):
        students = sql_query("SELECT * FROM students")

    if request.method == "GET":
        return render_template("admin/students.html", students=students)
    elif request.method == "POST":
        data = request.form

        if not data:
            return (
                render_template(
                    "admin/students.html",
                    students=students,
                    fail="Ingen data skickades.",
                ),
                400,
            )

        if not data["generate_codes"]:
            return (
                render_template(
                    "admin/students.html",
                    students=students,
                    fail="Felaktig data skickades.",
                ),
                400,
            )

        if not is_integer(data["generate_codes"]):
            return (
                render_template(
                    "admin/students.html",
                    students=students,
                    fail="Antal måste vara heltal",
                ),
                400,
            )

        if len(data["generate_codes"]) > 13:
            return (
                render_template(
                    "admin/students.html", students=students, fail="För stort tal."
                ),
                400,
            )

        # successful
        new_codes = generate_codes(data["generate_codes"])

        return render_template(
            "admin/students.html", new_codes=new_codes, success="Nya koder har skapats."
        )


# ------ add/remove school classes ------
@admin_routes.route("/classes", methods=["POST", "GET"])
@admin_required
def school_classes():
    template = "admin/school_classes.html"
    school_classes = sql_query("SELECT * FROM school_classes")

    if request.method == "GET":
        return render_template(template, school_classes=school_classes)

    if request.method == "POST":
        data = request.form

        if not data or len(data) != 2:
            return (
                render_template(
                    template, school_classes=school_classes, fail="Ingen data angiven."
                ),
                400,
            )

        # if adding
        if data["request_type"] == "add":
            if not data["class_name"]:
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="Saknar variabler.",
                    ),
                    400,
                )

            if not is_valid_input(data["class_name"]):
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="Innehåller ogiltiga tecken.",
                    ),
                    400,
                )

            if len(data["class_name"]) < 3 or len(data["class_name"]) > 10:
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="För kort/långt klassnamn.",
                    ),
                    400,
                )

            # create
            sql_query(
                f"INSERT INTO school_classes (class_name) VALUES ('{data['class_name']}')"
            )

            # re-fetch
            school_classes = sql_query("SELECT * FROM school_classes")

            return (
                render_template(
                    template, school_classes=school_classes, success="Ny klass skapad."
                ),
                201,
            )

        # if deleting
        if data["request_type"] == "delete":
            if not data["id"]:
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="Saknar variabler.",
                    ),
                    400,
                )

            if not is_integer(data["id"]):
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="Id måste vara heltal.",
                    ),
                    400,
                )

            # delete
            sql_query(f"DELETE FROM school_classes WHERE id={data['id']}")

            # re-fetch
            school_classes = sql_query("SELECT * FROM school_classes")

            return render_template(
                template, school_classes=school_classes, success="Klass raderad."
            )

        # if invalid request_type
        return (
            render_template(
                template, school_classes=school_classes, fail="Ogiltig förfrågan."
            ),
            400,
        )
