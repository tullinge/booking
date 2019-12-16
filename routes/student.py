# tullinge/booking
# https://github.com/tullinge/booking

# imports
import os
from flask import Blueprint, render_template, redirect, request, session

# google API (and auth)
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as requests_module

# components import
from components.core import (
    is_valid_input,
    basic_validation,
    is_integer,
    calculate_available_spaces,
)
from components.limiter_obj import limiter
from components.decorators import login_required, user_setup_completed, user_not_setup
from components.db import sql_query
from components.student import student_chosen_activity

# blueprint init
student_routes = Blueprint("student_routes", __name__, template_folder="../templates")

# variables
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", default=False)
GSUITE_DOMAIN_NAME = os.environ.get("GSUITE_DOMAIN_NAME", default=False)

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
@student_routes.route("/login")
@limiter.limit("200 per hour")
def students_login():
    return render_template("student/login.html", GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)


@student_routes.route("/callback", methods=["POST"])
def students_callback():
    if not basic_validation(["idtoken"]):
        return "Missing request data", 400

    token = request.form["idtoken"]

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return "Wrong issuer", 400
            # raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        if idinfo["hd"] != GSUITE_DOMAIN_NAME:
            return "Wrong hosted domain", 400
            # raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo["sub"]
    except ValueError:
        # Invalid token
        return "Invalid token", 400

    # user signed in
    r = requests_module.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if r.status_code is not requests_module.codes.ok:
        return "could not verify token", 400

    data = r.json()

    # verify
    if data["aud"] != GOOGLE_CLIENT_ID:
        return "'aud' is not valid!", 400

    existing_student = sql_query(
        f"SELECT * FROM students WHERE email='{data['email']}'"
    )

    # check if email exists in students
    if not existing_student:
        # create new object
        sql_query(
            f"INSERT INTO students (email, last_name, first_name) VALUES ('{data['email']}', '{data['family_name']}', '{data['given_name']}')"
        )
        existing_student = sql_query(
            f"SELECT * FROM students WHERE email='{data['email']}'"
        )

    session["fullname"] = f"{data['given_name']} {data['family_name']}"
    session["logged_in"] = True
    session["id"] = existing_student[0][0]

    return "Authenticated"


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
@limiter.limit("500 per hour")
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
        expected_values = ["class"]

        if not basic_validation(expected_values):
            return render_template(
                template, school_classes=school_classes, fail="Saknar/felaktig data."
            )

        school_class = request.form["class"]

        # check for length
        for k, v in request.form.items():
            if k == "class":
                if len(v) > 10 or len(v) > 50:
                    return (
                        render_template(
                            template,
                            school_classes=school_classes,
                            fail="Klassnamn får inte vara längre än 10 tecken.",
                        ),
                        400,
                    )

        # make sure to validate input variables against string authentication
        if not is_valid_input(
            school_class,
            allow_newline=False,
            allow_punctuation=False,
            allow_space=False,
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
            f"UPDATE students SET class = '{school_class}' WHERE id={session['id']}"
        )

        # if above fails, would raise exception
        session["school_class"] = school_class

        # redirect to index
        return redirect("/")


# selected activity
@student_routes.route("/activity/<id>", methods=["POST", "GET"])
@limiter.limit("500 per hour")
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
@limiter.limit("500 per hour")
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
