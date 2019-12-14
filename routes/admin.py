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
from components.admin import (
    get_activites_with_spaces,
    get_activity_questions_and_options,
)

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
@admin_routes.route("/activities", methods=["POST", "GET"])
@admin_required
def activities():
    template = "admin/activities.html"
    activities = get_activites_with_spaces()

    if request.method == "GET":
        return render_template("admin/activities.html", activities=activities)

    if request.method == "POST":
        data = request.form

        if not data:
            return (
                render_template(
                    template, activities=activities, fail="Ingen data skickades."
                ),
                400,
            )

        # creating activity
        if (
            not data["name"]
            or not data["spaces"]
            or not data["info"]
            or not len(data) == 3
        ):
            return (
                render_template(
                    template, activities=activities, fail="Felaktig data skickades."
                ),
                400,
            )

        # validate
        if not is_integer(data["spaces"]):
            return (
                render_template(
                    template,
                    activities=activities,
                    fail="Antalet platser måste vara ett heltal.",
                ),
                400,
            )

        if not is_valid_input(data["name"], allow_space=True) or not is_valid_input(
            data["info"], allow_space=True, allow_punctuation=True
        ):
            return (
                render_template(
                    template,
                    activities=activities,
                    fail="Data innehåller otillåtna tecken.",
                ),
                400,
            )

        # create
        sql_query(
            f"INSERT INTO activities (name, spaces, info) VALUES ('{data['name']}', {data['spaces']}, '{data['info']}')"
        )

        # re-fetch
        activities = get_activites_with_spaces()

        # success
        return render_template(
            template,
            activities=activities,
            success="Aktivitet skapad. Tryck på aktiviteten för att skapa frågor för aktiviteten.",
        )


# ------ selected activity ------
@admin_routes.route("/activity/<id>", methods=["POST", "GET"])
@admin_required
def selected_activity(id):
    template = "admin/activity.html"

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

    # get questions
    questions = get_activity_questions_and_options(id)

    if request.method == "GET":
        return render_template(
            template,
            activity=activity[0],
            questions=questions,
            available_spaces=calculate_available_spaces(id),
        )

    elif request.method == "POST":
        return "work in progress"


@admin_routes.route("/activity/<id>/students")
@admin_required
def activity_students(id):
    if not is_integer(id):
        return (
            render_template(
                "errors/custom.html", title="400", message="Id must be integer."
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

    # get students that have booked this activity and their answers
    query = sql_query(
        f"SELECT id, last_name, first_name, class FROM students WHERE chosen_activity={id}"
    )

    students = []
    for student in query:
        answer_query = sql_query(
            f"SELECT option_id, written_answer FROM answers WHERE student_id={student[0]}"
        )

        answers = []
        for answer in answer_query:
            if answer[0] is not None:
                option_name = sql_query(
                    f"SELECT text FROM options WHERE id={answer[0]}"
                )[0][0]
                answers.append(option_name)
            else:
                answers.append(answer[1])

        students.append((student, answers))

    questions = sql_query(f"SELECT question FROM questions WHERE activity_id={id}")

    return render_template(
        "admin/activity_students.html",
        students=students,
        activity=activity[0],
        questions=questions,
    )


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


# change password
@admin_routes.route("/changepassword", methods=["POST", "GET"])
@admin_required
def change_password():
    template = "admin/changepassword.html"

    # view page
    if request.method == "GET":
        return render_template(template)

    # change
    if request.method == "POST":
        data = request.form

        admin = sql_query(
            f"SELECT password FROM admins WHERE id={session.get('admin_id')}"
        )

        if not admin:
            return render_template(template, fail="Admin does not exist."), 400

        if (
            len(data) != 3
            or not data["current_password"]
            or not data["new_password"]
            or not data["new_password_verify"]
        ):
            return render_template(template, fail="Felaktig begäran."), 400

        if not verify_password(admin[0][0], data["current_password"]):
            return (
                render_template(template, fail="Felaktigt angivet nuvarande lösenord."),
                400,
            )

        if data["new_password"] != data["new_password_verify"]:
            return (
                render_template(
                    template, fail="Nya lösenordet måste vara likadant i båda fälten."
                ),
                400,
            )

        if len(data["new_password"]) <= 4:
            return (
                render_template(
                    template, fail="Lösenord för kort, måste vara längre än 4."
                ),
                400,
            )

        # update user
        sql_query(
            f"UPDATE admins SET password = '{hash_password(data['new_password'])}' WHERE id = {session.get('admin_id')}"
        )

        # change password
        return render_template(template, success="Lösenord bytt.")
