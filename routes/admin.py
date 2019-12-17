# tullinge/booking
# https://github.com/tullinge/booking

from flask import Blueprint, render_template, request, redirect, session

from components.db import sql_query
from components.core import (
    valid_input,
    integer_validation,
    hash_password,
    verify_password,
    calculate_available_spaces,
    is_integer,
)
from components.limiter_obj import limiter
from components.decorators import admin_required
from components.codes import generate_codes
from components.admin import (
    get_activites_with_spaces,
    get_activity_questions_and_options,
)

# blueprint init
admin_routes = Blueprint("admin_routes", __name__, template_folder="../templates")

BASEPATH = "/admin"

# admin login
@admin_routes.route("/login", methods=["GET", "POST"])
@limiter.limit("100 per hour")
def login():
    """
    Admin authentication

    * display login form (GET)
    * parse and validate data, login if correct password (POST)
    """

    if request.method == "GET":
        return render_template("admin/login.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # perform validation, login etc...
        if not valid_input(
            username, 4, 255, allow_space=False, allow_punctuation=False, swedish=False, allow_newline=False,
        ) or not valid_input(
            password, 8, 255, allow_space=False, allow_punctuation=False, swedish=False, allow_newline=False:
            return (
                render_template(
                    "admin/login.html", fail="Otilåten input."
                ),
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


# admin logout, pop session
@admin_routes.route("/logout")
@admin_required
def logout():
    """
    Destroy admin session and set admin_id as invalid
    """
    session.pop("admin_logged_in", False)
    session.pop("admin_id", None)

    return redirect(f"{BASEPATH}/login")


# index
@admin_routes.route("/")
@admin_required
def index():
    """
    Admin index
    """

    amount_activities = len(sql_query("SELECT * FROM activities"))
    amount_codes = len(sql_query("SELECT * FROM students"))
    amount_students_setup = sql_query(
        "SELECT COUNT(chosen_activity) FROM students WHERE chosen_activity <> NULL;"
    )
    amount_students_setup = amount_students_setup[0][0]

    return render_template(
        "admin/index.html",
        amount_activities=amount_activities,
        amount_codes=amount_codes,
        amount_students_setup=amount_students_setup,
    )


# activities
@admin_routes.route("/activities", methods=["POST", "GET"])
@admin_required
def activities():
    """
    Activities management

    * list available activities (GET)
    * create new activities (POST)
    """

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

        # validate
        if not integer_validation(data["spaces"], 3, 3):
            return (
                render_template(
                    template,
                    activities=activities,
                    fail="Otilåten input.",
                ),
                400,
            )
        if not valid_input(
            data["name"], 4, 255, allow_newline=False,
        ) or not valid_input(
            data["info"], 4, 255, allow_newline=False,
        ):
            return (
                render_template(
                    activities=activities,
                    fail="Otilåten input."
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


# selected activity
@admin_routes.route("/activity/<id>", methods=["POST", "GET"])
@admin_required
def selected_activity(id):
    """
    Manage specific activity

    * display activity information (GET)
    * display questions attatched to this activity (GET)
    * create new questions for this activity (POST)
    """

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
        data = request.form

        if not data or not data["question"]:
            print(data["question"])
            return (
                render_template(
                    template,
                    activity=activity[0],
                    questions=questions,
                    available_spaces=calculate_available_spaces(id),
                    fail="Ingen data skickades/saknar data.",
                ),
                400,
            )

        # is written answer
        if request.form.get("written_answer"):
            sql_query(
                f"INSERT INTO questions (activity_id, question, written_answer) VALUES ({id}, '{data['question']}', 1)"
            )

            # re-fetch
            questions = get_activity_questions_and_options(id)

            return render_template(
                template,
                activity=activity[0],
                questions=questions,
                available_spaces=calculate_available_spaces(id),
                success="Fråga skapad.",
            )

        # admin is creating question with options
        sql_query(
            f"INSERT INTO questions (activity_id, question, written_answer) VALUES ({id}, '{data['question']}', 0)"
        )

        # re-fetch
        questions = get_activity_questions_and_options(id)

        return render_template(
            template,
            activity=activity[0],
            questions=questions,
            available_spaces=calculate_available_spaces(id),
            success="Fråga skapad. Tryck på frågan nedan för att lägga till svarsalternativ.",
        )


# view question
@admin_routes.route("/question/<id>", methods=["POST", "GET"])
@admin_required
def question_id(id):
    """
    Manage question options, requires specific question id
    question must not be of type written_answer

    * list existing options for this question (GET)
    * create new options for this question (POST)
    """

    template = "admin/view_question.html"

    if not is_integer(id):
        return (
            render_template(
                "errors/custom.html", title="400", message="Id must be integer."
            ),
            400,
        )

    question = sql_query(f"SELECT * FROM questions WHERE id={id}")

    if not question:
        return (
            render_template(
                "errors/custom.html", title="400", message="Question does not exist."
            ),
            400,
        )

    if question[0][3]:
        return (
            render_template(
                "errors/custom.html",
                title="400",
                message="Question is not correct type.",
            ),
            400,
        )

    # get options
    options = sql_query(f"SELECT * FROM options WHERE question_id={question[0][0]}")

    if request.method == "GET":
        return render_template(template, question=question[0], options=options)

    if request.method == "POST":
        data = request.form

        if not valid_input(
            data["text"], 0, 511, allow_newline=False
            ):
            return (
                render_template(
                    template,
                    question=question[0],
                    options=options,
                    fail="Otilåten input.",
                ),
                400,
            )

        # add option
        sql_query(
            f"INSERT INTO options (question_id, text) VALUES ({id}, '{data['text']}')"
        )

        # re-fetch
        options = sql_query(f"SELECT * FROM options WHERE question_id={question[0][0]}")

        return render_template(
            template,
            question=question[0],
            options=options,
            success="Alternativ skapat.",
        )


# booked students to specific activity
@admin_routes.route("/activity/<id>/students")
@admin_required
def activity_students(id):
    """
    Students booked to activity

    * display all students booked to this activity (GET)
        - along with any answers to questions available for this activity
    * (hopefully) printer friendly
    """

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


# admin user management
@admin_routes.route("/users", methods=["GET", "POST"])
@admin_required
def admin_users():
    """
    Admin user management

    * list all existing admin users (GET)
    * delete existing admin users (POST)
    * create new admin users (POST)
    """

    template = "admin/users.html"
    query = "SELECT id, name, username FROM admins"
    admins = sql_query(query)

    if request.method == "GET":
        return render_template(template, admins=admins)

    if request.method == "POST":
        data = request.form

        if not data:
            return (
                render_template(template, admins=admins, fail="Ogiltig begäran."),
                400,
            )

        # delete
        if data["request_type"] == "delete":
            if len(data) != 2 or not data["id"]:
                return (
                    render_template(template, admins=admins, fail="Saknar data."),
                    400,
                )

            if not is_integer(data["id"]):
                return (
                    render_template(
                        template, admins=admins, fail="Id måste vara heltal."
                    ),
                    400,
                )

            # cannot delete self
            if int(data["id"]) == int(session.get("admin_id")):
                return (
                    render_template(
                        template,
                        admins=admins,
                        fail="Kan inte radera den egna användaren.",
                    ),
                    400,
                )

            # delete user
            sql_query(f"DELETE FROM admins WHERE id={data['id']}")

            # update admins
            admins = sql_query(query)

            return render_template(
                template, admins=admins, success="Användare raderad."
            )

        if data["request_type"] == "add":
            
            if not valid_input(
                data["name"],
                allow_newline=False,
                allow_punctuation=False
            ):
                return (
                    render_template(
                        template, admins=admins, fail="Ogiltigt namn."
                    ),
                    400,
                )

            if not valid_input(
                data["username"],
                allow_space=False,
                allow_newline=False,
                swedish=False,
                allow_punctuation=False,
            ):
                return (
                    render_template(
                        template, admins=admins, fail="Ogiltigt användarnamn."
                    ),
                    400,
                )

            # check for length
            for k, v in data.items():
                if (
                    len(v) >= 255 or len(v) < 4 and k != "request_type"
                ):  # request_type is ignored from this validation
                    return (
                        render_template(
                            template,
                            admins=admins,
                            fail=f"{k} för kort eller för långt (4-255).",
                        ),
                        400,
                    )

                if k == "password":
                    if len(v) < 8:
                        return (
                            render_template(
                                template,
                                admins=admins,
                                fail="Lösenordet måste vara minst 8 karaktärer långt.",
                            ),
                            400,
                        )

            # create new user
            sql_query(
                f"INSERT INTO admins (name, username, password) VALUES ('{data['name']}', '{data['username']}', '{hash_password(data['password'])}')"
            )

            # re-fetch
            admins = sql_query(query)

            return render_template(
                template, admins=admins, success="Nytt konto skapats."
            )

        return render_template(template, admins=admins, fail="Felaktig begäran."), 400


# student codes
@admin_routes.route("/students", methods=["GET", "POST"])
@admin_required
def students():
    """
    Student account management

    * list all students/codes (GET)
    * create new codes, show them to admin (POST)
    """

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


# school classes management
@admin_routes.route("/classes", methods=["POST", "GET"])
@admin_required
def school_classes():
    """
    School classes management

    * list available school_classes (GET)
    * create new school_classes (POST)
    * delete existing school_classes (POST)
    """

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
            
            class_check = sql_query(
                f"""SELECT * FROM `school_classes` WHEAR `class_name` = BINARY '{data["class_name"]}' """
                )

            if class_check:
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail="klass finns redan.",
                    ),
                    400,
                )
            if not valid_input(
                data["class_name"], 3, 10, allow_space=False, allow_punctuation=False, swedish=False, allow_newline=False,
            ):
                return (
                    render_template(
                        school_classes=school_classes,
                        fail="Otilåten input."
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


# show students per class
@admin_routes.route("/classes/<id>/students")
@admin_required
def student_classes(id):
    """
    Show students registrered to class

    * display list of all students (GET)
    """

    template = "admin/class_students.html"

    if not is_integer(id):
        return (
            render_template(
                "errors/custom.html", title="400", message="Id must be integer"
            ),
            400,
        )

    school_class = sql_query(f"SELECT * FROM school_classes WHERE id={id}")

    if not school_classes:
        return (
            render_template(
                "errors/custom.html", title="400", message="Class does not exist."
            ),
            400,
        )

    # show students with  class defined as this one
    students = sql_query(
        f"SELECT id, first_name, last_name, class, chosen_activity FROM students WHERE class='{school_class[0][1]}'"
    )

    return render_template(template, school_class=school_class[0], students=students)


# change password
@admin_routes.route("/changepassword", methods=["POST", "GET"])
@admin_required
def change_password():
    """
    Change account password

    * display form (GET)
    * change password for logged in admin (POST)
    """
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

        if len(data["new_password"]) < 8:
            return (
                render_template(
                    template,
                    fail="Lösenord för kort, måste vara längre än 8 karaktärer.",
                ),
                400,
            )

        # update user
        sql_query(
            f"UPDATE admins SET password = '{hash_password(data['new_password'])}' WHERE id = {session.get('admin_id')}"
        )

        # change password
        return render_template(template, success="Lösenord bytt.")
