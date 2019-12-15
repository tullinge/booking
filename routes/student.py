# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import Blueprint, render_template, redirect, request, session

# components import
from components.core import is_valid_input, is_integer, calculate_available_spaces
from components.decorators import login_required, user_setup_completed, user_not_setup
from components.db import sql_query
from components.student import student_chosen_activity

# blueprint init
student_routes = Blueprint("student_routes", __name__, template_folder="../templates")


# index
@student_routes.route("/")
@login_required
@user_setup_completed
def index():
    """
    Student index

    * list available activities (GET)
        - along with information about them (also how many spaces available)
    """

    chosen_activity = student_chosen_activity()
    query = sql_query("SELECT * FROM activities")

    activities = []
    for activity in query:
        activities.append((activity, calculate_available_spaces(activity[0])))

    return render_template(
        "student/index.html",
        fullname=session.get("fullname"),
        school_class=session.get("school_class"),
        activities=activities,
        chosen_activity=chosen_activity[1],
    )


# login
@student_routes.route("/login", methods=["GET", "POST"])
def students_login():
    """
    Student authentication

    * display login form (GET)
    * validate and parse data, login if success (POST)
    """

    if request.method == "GET":
        return render_template("student/login.html")
    else:
        password = request.form["password"].upper()

        if not password:
            return render_template("student/login.html", fail="Saknar lösenord."), 400

        if not len(password) == 8:
            return render_template("student/login.html", fail="Fel längd."), 400

        if not is_valid_input(
            password,
            allow_newline=False,
            allow_space=False,
            allow_punctuation=False,
            swedish=False,
        ):
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


# logout
@student_routes.route("/logout")
@login_required
def logout():
    """
    Student logout

    * destory user session (GET)
    """

    session.pop("logged_in", False)
    session.pop("id", None)

    return redirect("/login")


# setup
@student_routes.route("/setup", methods=["POST", "GET"])
@login_required
@user_not_setup
def setup():
    """
    Student setup

    * only show page if student has not yet configured it's user (GET)
    * add first_name, last_name and school_class to student object (POST)
    """

    template = "student/setup.html"
    school_classes = sql_query("SELECT * FROM school_classes")

    if request.method == "GET":
        return render_template(template, school_classes=school_classes)
    elif request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        school_class = request.form["class"]

        # all input variables need to be present
        if not first_name or not last_name or not school_class:
            return (
                render_template(
                    template, school_classes=school_classes, fail="Saknar variabler.",
                ),
                400,
            )

        # check for length
        for k, v in request.form.items():
            if len(v) < 1 or len(v) > 50:
                return (
                    render_template(
                        template,
                        school_classes=school_classes,
                        fail=f"{k} är för lång eller för kort (1-50).",
                    ),
                    400,
                )

            if k == "class":
                if len(v) > 10:
                    return (
                        render_template(
                            template,
                            school_classes=school_classes,
                            fail="Klassnamn får inte vara längre än 10 tecken.",
                        ),
                        400,
                    )

        # make sure to validate input variables against string authentication
        if (
            not is_valid_input(first_name, allow_newline=False)
            or not is_valid_input(last_name, allow_newline=False)
            or not is_valid_input(
                school_class,
                allow_newline=False,
                allow_punctuation=False,
                allow_space=False,
            )
        ):
            return (
                render_template(
                    "student/setup.html",
                    school_classes=school_classes,
                    fail="Icke tillåtna karaktärer. Endast alfabetet och siffror tillåts.",
                ),
                400,
            )

        # verify that the school_class provided by the user actually is valid
        if school_class not in str(
            school_classes
        ):  # poorly validated, but should be sufficient
            return render_template(
                template,
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


# selected activity
@student_routes.route("/activity/<id>", methods=["POST", "GET"])
@login_required
@user_setup_completed
def selected_activity(id):
    """
    Selected activity

    * show activity information (GET)
    * book student to activity, if available spaces are still left (POST)
    """

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
            "student/activity.html",
            activity=activity[0],
            fullname=session.get("fullname"),
            school_class=session.get("school_class"),
            questions=questions,
            available_spaces=calculate_available_spaces(id),
        )

    if request.method == "POST":
        for k, v in request.form.items():
            if not v:
                return (
                    render_template(
                        "student/activity.html",
                        activity=activity[0],
                        fullname=session.get("fullname"),
                        school_class=session.get("school_class"),
                        questions=questions,
                        available_spaces=calculate_available_spaces(id),
                        fail="Saknar data.",
                    ),
                    400,
                )

            if not is_integer(k):
                return (
                    render_template(
                        "student/activity.html",
                        activity=activity[0],
                        fullname=session.get("fullname"),
                        school_class=session.get("school_class"),
                        questions=questions,
                        available_spaces=calculate_available_spaces(id),
                        fail="Felaktigt skickad data.",
                    ),
                    400,
                )

            if not is_valid_input(
                k,
                allow_newline=False,
                allow_punctuation=False,
                allow_space=False,
                swedish=False,
            ) or not is_valid_input(v, allow_newline=False):
                return (
                    render_template(
                        "student/activity.html",
                        activity=activity[0],
                        fullname=session.get("fullname"),
                        school_class=session.get("school_class"),
                        questions=questions,
                        available_spaces=calculate_available_spaces(id),
                        fail="Innehåller ogiltiga tecken.",
                    ),
                    400,
                )

        # check if it still has available_spaces
        if calculate_available_spaces(id) < 1:
            return (
                render_template(
                    "student/activity.html",
                    activity=activity[0],
                    fullname=session.get("fullname"),
                    school_class=session.get("school_class"),
                    questions=questions,
                    available_spaces=calculate_available_spaces(id),
                    fail="Denna aktivitet har inga lediga platser.",
                ),
                400,
            )

        # delete any previous answers this user has submitted
        sql_query(f"DELETE FROM answers WHERE student_id={session.get('id')}")

        # validation completed
        for question_id, answer in request.form.items():
            # check if question is of type written or not
            question = sql_query(f"SELECT * FROM questions WHERE id={question_id}")[0]

            if question[3]:
                # written answers
                sql_query(
                    f"""
                        INSERT INTO answers (student_id, question_id, written_answer)
                            VALUES ({session.get('id')}, {question_id}, '{str(answer)}')
                        ;
                    """
                )
            else:
                # option
                sql_query(
                    f"""
                        INSERT INTO answers (student_id, question_id, option_id)
                            VALUES ({session.get('id')}, {question_id}, {answer})
                        ;
                    """
                )

        # set chosen_activity
        sql_query(
            f"""
                UPDATE students
                SET chosen_activity={int(id)}
                WHERE id={session.get('id')}
            """
        )

        return redirect("/confirmation")


# confirmation
@student_routes.route("/confirmation")
@login_required
@user_setup_completed
def confirmation():
    """
    Confirmation page

    * confirm the students new booking (GET)
    """

    activity = student_chosen_activity()

    return render_template(
        "student/confirmation.html",
        fullname=session.get("fullname"),
        school_class=session.get("school_class"),
        activity=activity[1],
    )
