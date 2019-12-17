# tullinge/booking
# https://github.com/tullinge/booking

# imports
from flask import Blueprint, render_template, redirect, request, session, jsonify

# google API (and auth)
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as requests_module
from components.google import GOOGLE_CLIENT_ID, GSUITE_DOMAIN_NAME

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
    return render_template("student/login.html")


@student_routes.route("/callback", methods=["POST"])
def students_callback():
    if not request.get_json("idtoken"):
        return (
            jsonify({"status": False, "code": 400, "message": "missing form data"}),
            400,
        )

    token = request.json["idtoken"]

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
            return (
                jsonify({"status": False, "code": 400, "message": "Invalid issuer."}),
                400,
            )
            # raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        if idinfo["hd"] != GSUITE_DOMAIN_NAME:
            return (
                jsonify(
                    {"status": False, "code": 400, "message": "Wrong hosted domain."}
                ),
                400,
            )
            # raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo["sub"]
    except ValueError:
        # Invalid token
        return jsonify({"status": False, "code": 400, "message": "Invalid token."}), 400

    # user signed in
    r = requests_module.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")

    if r.status_code is not requests_module.codes.ok:
        return (
            jsonify(
                {"status": False, "code": 400, "message": "Could not verify token."}
            ),
            400,
        )

    data = r.json()

    # verify
    if data["aud"] != GOOGLE_CLIENT_ID:
        return (
            jsonify({"status": False, "code": 400, "message": "'aud' is invalid!."}),
            400,
        )

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

    return jsonify({"status": True, "code": 200, "message": "authenticated"}), 400


@student_routes.route("/callback/error", methods=["POST"])
def callback_error():
    return render_template(
        "student/callback_error.html", message=request.form.get("message")
    )


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

    if request.method == "GET":
        return render_template(template)
    elif request.method == "POST":
        expected_values = ["join_code"]

        if not basic_validation(expected_values):
            return render_template(template, fail="Saknar/felaktig data.")

        join_code = request.form["join_code"]

        if len(join_code) != 8:
            return render_template(template, fail="Fel längd på kod."), 40

        # make sure to validate input variables against string authentication
        if not is_valid_input(
            join_code, allow_newline=False, allow_punctuation=False, allow_space=False,
        ):
            return (
                render_template(template, fail="Icke tillåtna karaktärer.",),
                400,
            )

        # verify code
        school_class = sql_query(
            f"SELECT * FROM school_classes WHERE password='{join_code}'"
        )

        if not school_class:
            return render_template(template, fail="Felaktig kod.",), 400

        # passed validation, update user variables
        sql_query(
            f"UPDATE students SET class_id={school_class[0][0]}  WHERE id={session['id']}"
        )

        # if above fails, would raise exception
        session["school_class"] = school_class[0][1]

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
